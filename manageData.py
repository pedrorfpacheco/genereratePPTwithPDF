import json
import re
import ollama


class OllamaProcessor:
    """Class for processing text using Ollama models"""

    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def clean_and_structure_text(self, text):
        """
        Uses Ollama to clean and structure poorly formatted text.

        Args:
            text (str): Text extracted from the PDF.

        Returns:
            str: Cleaned and structured text.
        """
        prompt = f"""
                Please clean and structure the following raw text extracted from a **procedural document** (e.g., a manual, guide, or technical specification).
                The text may contain OCR artifacts, incorrect line breaks, extra spaces, and mixed formatting.

                Your primary goal is to make the text highly readable and usable for further processing, while **strictly preserving all procedural formatting elements**:
                - **Numbered lists** (e.g., 1., 2., 3.)
                - **Bullet points** (e.g., -, *, •)
                - **Headings and subheadings** (e.g., "1. Introduction", "2.1 Setup")
                - **Important notes, warnings, or tips** (if identifiable).

                Remove any unnecessary whitespace, merge broken lines logically, and fix common OCR errors if obvious.

                TEXT:
                {text}

                Return ONLY the cleaned and well-formatted text. Do not add any conversational filler or explanations.
                """

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])
            cleaned_text = response['message']['content']
            return cleaned_text
        except Exception as e:
            print(f"Error using Ollama to clean text: {e}")
            return text

    def analyze_document_structure(self, text):
        prompt = f"""
        Analyze this document and extract its structure. Identify the title, subtitle, version, date, and sections.
        For each section, identify its title and main points.

        DOCUMENT:
        {text[:8000]}

        Return the result as a JSON object with the following structure:
        {{
            "title": "Document Title",
            "subtitle": "Subtitle if it exists",
            "version": "Version if mentioned",
            "date": "Date if mentioned",
            "sections": [
                {{
                    "title": "Section Name 1",
                    "content": ["Point 1", "Point 2", "..."]
                }},
                {{
                    "title": "Section Name 2", 
                    "content": ["Point 1", "Point 2", "..."]
                }}
            ]
        }}

        Use valid JSON format with no trailing commas. Do not include extra explanations, only the JSON.
        """

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])

            if not response or 'message' not in response or not response['message'].get('content'):
                raise ValueError("Ollama API response is empty or invalid.")

            result = response['message']['content']

            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', result)
            if json_match:
                result = json_match.group(1)

            result = re.sub(r'^[^{]*', '', result)
            result = re.sub(r'[^}]*$', '', result)

            result = re.sub(r',\s*}', '}', result)
            result = re.sub(r',\s*]', ']', result)

            try:
                import json
                structure = json.loads(result)
                return structure
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print(f"Received response: {result}")

                try:
                    import json5
                    structure = json5.loads(result)
                    return structure
                except:
                    return {
                        "title": "Extracted Document",
                        "subtitle": "",
                        "version": "",
                        "date": "",
                        "sections": [{
                            "title": "General Information",
                            "content": ["The document could not be properly parsed."]
                        }]
                    }
        except Exception as e:
            print(f"Error analyzing structure with Ollama: {e}")
            print(
                f"Received response: {response['message']['content'] if 'response' in locals() and response and 'message' in response else 'No response'}")

            return {
                "title": "Extracted Document",
                "subtitle": "",
                "version": "",
                "date": "",
                "sections": [{
                    "title": "General Information",
                    "content": ["The document could not be properly parsed."]
                }]
            }

    def generate_slide_content(self, section_text, section_title):
        """
        Uses Ollama to generate slide content from a section's text.

        Args:
            section_text (str): Text of the section.
            section_title (str): Title of the section.

        Returns:
            list: List of bullet points for the slide.
        """
        prompt = f"""
        Create content for a PowerPoint slide based on the following text from the section "{section_title}".
        Extract 3-5 main points that are clear and concise.

        SECTION TEXT:
        {section_text}

        Return only the points, one per line, without numbering or bullet points.
        """

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])

            content = response['message']['content']

            points = [line.strip() for line in content.split('\n') if line.strip()]

            cleaned_points = []
            for point in points:
                point = re.sub(r'^[\*\-•\d]+[\.\)]\s*', '', point)
                if point:
                    cleaned_points.append(point)

            return cleaned_points
        except Exception as e:
            print(f"Error generating slide content with Ollama: {e}")
            sentences = re.split(r'[.!?]+', section_text)
            return [s.strip() for s in sentences if len(s.strip()) > 20][:5]