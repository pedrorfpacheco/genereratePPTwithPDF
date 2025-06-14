import json
import re
import ollama


class OllamaProcessor:

    def __init__(self, model_name="llama3"):
        self.model_name = model_name

    def clean_and_structure_text(self, text):
        prompt = f"""
        Please clean and structure the following raw text extracted from a **procedural document** (e.g., a manual, guide, or technical specification).
        The text may contain OCR artifacts, incorrect line breaks, extra spaces, and mixed formatting.

        Your primary goal is to make the text highly readable and usable for further processing, while **strictly preserving all procedural formatting elements**:
        - **Numbered lists** (e.g., 1., 2., 3.)
        - **Bullet points** (e.g., -, *, •)
        - **Headings and subheadings** (e.g., "1. Introduction", "2.1 Setup")
        - **Important notes, warnings, or tips** (if identifiable).

        **Specific instructions**:
        1. Remove unnecessary whitespace and merge broken lines logically.
        2. Fix common OCR errors (e.g., incorrect characters, misplaced symbols) if they are obvious.
        3. Ensure that procedural elements (lists, headings, notes) are preserved and formatted correctly.
        4. Maintain the logical flow of the document, ensuring readability and usability.

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
        Analyze the following document and transform it into a structure optimized for a slide presentation.

        DOCUMENT:
        {text[:8000]}

        Return a JSON object with the following structure:
        {{
            "title": "Document Title",
            "subtitle": "Subtitle (if available)",
            "version": "Version (if mentioned)",
            "date": "Date (if mentioned)",
            "sections": [
                {{
                    "title": "Section Title",
                    "content": ["Point 1", "Point 2", "..."],
                    "importance": "high|medium|low",
                    "type": "overview|procedure|warning|summary"
                }}
            ]
        }}

        **Guidelines**:
        1. **Purpose**: The presentation should effectively communicate the document's key points to an audience. Focus on clarity, conciseness, and visual impact.
        2. **Content Selection**:
           - Identify the most important topics and ideas from the document.
           - Prioritize information that is relevant to the audience and purpose of the presentation.
        3. **Content Transformation**:
           - Preserve concise lists that are already suitable for slides.
           - Break down lengthy paragraphs into key points of 1-2 lines each.
           - Summarize detailed instructions into main steps.
           - Simplify complex concepts into visually digestible points.
        4. **Length Control**:
           - Ensure each point is short enough to fit on a slide (maximum 2 lines).
           - If necessary, split long points into smaller, more manageable ones.
        5. **Structure and Flow**:
           - Organize sections in a logical order to create a narrative flow.
           - Use headings and subheadings to guide the audience through the content.
        6. **Classification**:
           - Assess the importance of each section (high/medium/low) based on its relevance to the presentation.
           - Classify the type of each section (overview, procedure, warning, summary) to guide its visual representation.
        7. **Output**:
           - Return only valid JSON, without additional explanations or comments.
           - Ensure the JSON is well-structured and adheres to the specified format.
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

    def analyze_document_with_images(self, text, image_data):
        """
        Analisa o documento considerando o texto e as imagens disponíveis para criar uma estrutura
        que associa imagens a seções específicas do documento.

        Args:
            text (str): O texto do documento
            image_data (list): Lista de dicionários contendo informações das imagens extraídas

        Returns:
            dict: Estrutura do documento com imagens associadas às seções
        """
        # Primeiro, obtemos a estrutura básica do documento
        doc_structure = self.analyze_document_structure(text)

        if not image_data or not isinstance(image_data, list) or len(image_data) == 0:
            return doc_structure

        # Preparar um resumo das imagens para o prompt
        image_summary = []
        for i, img in enumerate(image_data[:10]):  # Limitamos a 10 imagens para o prompt
            page_num = img.get("page_num", "desconhecida")
            dimensions = f"{img.get('width', 0)}x{img.get('height', 0)}"
            image_summary.append(f"Imagem {i + 1}: Página {page_num + 1}, Dimensões {dimensions}")

        image_info = "\n".join(image_summary)

        # Criamos um prompt para analisar a relação entre texto e imagens
        prompt = f"""
        Analise este documento que contém texto e imagens. Preciso entender como as imagens se relacionam 
        com o conteúdo textual para criar slides eficazes.

        DOCUMENTO (resumo do texto):
        {text[:2000]}...

        IMAGENS DISPONÍVEIS:
        {image_info}

        Baseado no texto do documento, analise como estas imagens provavelmente se relacionam ao conteúdo.
        Para cada seção do documento, indique:
        1. Quais imagens provavelmente estão relacionadas a esta seção
        2. Como estas imagens devem ser apresentadas (ao lado do texto, como fundo, etc.)
        3. Se a seção possui referências explícitas a figuras, gráficos ou diagramas

        Formato de resposta (JSON):
        {{
            "sections": [
                {{
                    "title": "Título da Seção",
                    "relevant_images": [0, 2],  // Índices das imagens relevantes (0-indexed)
                    "image_references": ["Figura 1", "Gráfico 2.1"],  // Referências textuais a imagens
                    "presentation_style": "side-by-side"  // Como apresentar (side-by-side, background, standalone)
                }}
            ]
        }}
        """

        try:
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])

            if not response or 'message' not in response:
                raise ValueError("Resposta da API Ollama vazia ou inválida")

            result = response['message']['content']

            # Extrair JSON da resposta
            json_match = re.search(r'```json\s*([\s\S]*?)\s*```', result)
            if json_match:
                result = json_match.group(1)

            result = re.sub(r'^[^{]*', '', result)
            result = re.sub(r'[^}]*$', '', result)

            try:
                import json
                image_analysis = json.loads(result)

                # Agora, enriquecemos a estrutura original do documento com as informações sobre imagens
                sections_with_images = {}
                for section in image_analysis.get("sections", []):
                    section_title = section.get("title")
                    if section_title:
                        sections_with_images[section_title] = {
                            "relevant_images": section.get("relevant_images", []),
                            "image_references": section.get("image_references", []),
                            "presentation_style": section.get("presentation_style", "side-by-side")
                        }

                # Adicionar informações de imagens à estrutura do documento
                for section in doc_structure.get("sections", []):
                    section_title = section.get("title")
                    if section_title in sections_with_images:
                        section["image_info"] = sections_with_images[section_title]
                        section["has_images"] = True
                    else:
                        section["has_images"] = False

                return doc_structure

            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON da análise de imagens: {e}")
                return doc_structure

        except Exception as e:
            print(f"Erro ao analisar documento com imagens: {e}")
            return doc_structure