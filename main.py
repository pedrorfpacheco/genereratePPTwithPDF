import os
import threading
import time

from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename

from manageData import OllamaProcessor
from ppt_generator import PdfToPptxConverter
from readPDF import PdfExtractor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def pdf_to_pptx_with_ollama(pdf_path=None, pdf_text=None, output_file=None, model_name="llama3", theme="default"):
    print(f"Starting processing with model: {model_name}")
    ollama_processor = OllamaProcessor(model_name=model_name)

    # Configuração do arquivo de saída
    if not output_file:
        if pdf_path:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_file = f"{base_name}.pptx"
        else:
            output_file = "presentation.pptx"

    # Obtenção do texto do documento
    text = pdf_text
    document_name = "Document"

    if not text and pdf_path:
        print(f"Extracting text from PDF: {pdf_path}")
        try:
            extractor = PdfExtractor()
            text = extractor.extract_text(pdf_path)
            document_name = os.path.splitext(os.path.basename(pdf_path))[0]
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            raise ValueError(f"Failure to extract text: {str(e)}")

    if not text or len(text.strip()) < 10:
        raise ValueError("Insufficient text for processing")

    try:
        # Limpeza e estruturação do texto
        print("Cleaning up and structuring the text...")
        cleaned_text = ollama_processor.clean_and_structure_text(text)

        # Análise estrutural do documento
        print("Analyzing the structure of the document...")
        document_structure = ollama_processor.analyze_document_structure(cleaned_text)

        # Validação e processamento da estrutura
        document_structure = normalize_document_structure(document_structure, document_name, text)

        # Geração da apresentação
        print(f"Generating presentation with theme '{theme}'...")
        converter = PdfToPptxConverter(output_file, ollama_processor, theme=theme)
        converter.create_presentation(document_structure)

        print(f"Presentation successfully generated: {output_file}")
        return output_file

    except Exception as e:
        print(f"Error during processing: {str(e)}")
        # Tentativa de recuperação de erro
        try:
            print("Trying alternative generation method...")
            fallback_structure = create_fallback_structure(text, document_name)

            converter = PdfToPptxConverter(output_file, ollama_processor, theme=theme)
            converter.create_presentation(fallback_structure)

            print(f"Presentation generated via alternative method: {output_file}")
            return output_file
        except Exception as fallback_error:
            print(f"Total processing failure: {str(fallback_error)}")
            raise ValueError(f"The presentation could not be generated.: {str(e)}")


def normalize_document_structure(structure, document_name, original_text):
    if isinstance(structure, str):
        try:
            import json
            structure = json.loads(structure)
        except json.JSONDecodeError:
            return create_fallback_structure(original_text, document_name)

    if not isinstance(structure, dict):
        return create_fallback_structure(original_text, document_name)

    normalized = {
        "title": structure.get("title", document_name),
        "subtitle": structure.get("subtitle", ""),
        "version": structure.get("version", ""),
        "date": structure.get("date", ""),
        "sections": []
    }

    sections = structure.get("sections", [])
    if not sections:
        paragraphs = [p for p in original_text.split('\n\n') if p.strip()]
        if paragraphs:
            normalized["sections"] = [{
                "title": "Main Content",
                "content": paragraphs[:10],  # Primeiros 10 parágrafos
                "importance": "high",
                "type": "overview"
            }]
    else:
        for section in sections:
            if not isinstance(section, dict):
                continue

            normalized_section = {
                "title": section.get("title", "Untitled Section"),
                "content": section.get("content", []),
                "importance": section.get("importance", "medium"),
                "type": section.get("type", "overview")
            }

            if isinstance(normalized_section["content"], str):
                normalized_section["content"] = [normalized_section["content"]]

            normalized_section["content"] = [item for item in normalized_section["content"] if
                                             item and isinstance(item, str)]

            if normalized_section["content"]:
                normalized["sections"].append(normalized_section)

    return normalized


def create_fallback_structure(text, document_name):
    fallback = {
        "title": document_name,
        "subtitle": "",
        "version": "",
        "date": "",
        "sections": []
    }

    lines = text.split('\n')

    potential_titles = []
    for i, line in enumerate(lines):
        line = line.strip()
        if line and 10 <= len(line) <= 100:
            if line.isupper() or line.endswith(':') or line.startswith('#'):
                potential_titles.append((i, line.lstrip('#').strip()))

    if potential_titles:
        for i in range(len(potential_titles)):
            start_idx = potential_titles[i][0] + 1
            end_idx = potential_titles[i + 1][0] if i < len(potential_titles) - 1 else len(lines)

            section_title = potential_titles[i][1]
            section_content = [l.strip() for l in lines[start_idx:end_idx] if l.strip()]

            paragraphs = []
            current = []
            for line in section_content:
                if len(line) < 3:
                    if current:
                        paragraphs.append(' '.join(current))
                        current = []
                else:
                    current.append(line)
            if current:
                paragraphs.append(' '.join(current))

            if paragraphs:
                fallback["sections"].append({
                    "title": section_title,
                    "content": paragraphs[:7],
                    "importance": "medium",
                    "type": "overview"
                })

    if not fallback["sections"]:
        paragraphs = []
        current = []
        for line in lines:
            line = line.strip()
            if not line:
                if current:
                    paragraphs.append(' '.join(current))
                    current = []
            else:
                current.append(line)
        if current:
            paragraphs.append(' '.join(current))

        paragraphs = [p for p in paragraphs if len(p) > 20]

        if paragraphs:
            fallback["sections"].append({
                "title": "Document Content",
                "content": paragraphs[:10],
                "importance": "high",
                "type": "overview"
            })

    return fallback


def pdf_bytes_to_pptx(pdf_bytes, output_file="presentation.pptx", model_name="llama3", theme="default"):
    temp_pdf_path = "temp_pdf_file.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(pdf_bytes)

    try:
        result = pdf_to_pptx_with_ollama(pdf_path=temp_pdf_path, output_file=output_file,
                                         model_name=model_name, theme=theme)
        return result
    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['pdf_file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and allowed_file(file.filename):
        model_name = request.form.get('model', 'llama3')
        theme = request.form.get('theme', 'default')

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()

            output_filename = os.path.splitext(filename)[0] + '.pptx'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

            pdf_bytes_to_pptx(pdf_bytes, output_file=output_path, model_name=model_name, theme=theme)

            response = send_file(output_path,
                                 as_attachment=True,
                                 download_name=output_filename,
                                 mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')

            def delayed_file_removal(filepath, delay=3):
                time.sleep(delay)
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"File removed successfully: {filepath}")
                except Exception as e:
                    print(f"Error removing file: {str(e)}")

            threading.Thread(target=delayed_file_removal, args=(output_path,)).start()

            return response

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            if 'output_path' in locals() and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except (PermissionError, FileNotFoundError):
                    pass
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500

        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    else:
        return jsonify({'error': 'File type not allowed. Please upload a PDF.'}), 400


@app.route('/models')
def get_models():
    models = [
        {"id": "llama3.2:1b", "name": "Llama 3.2 (1B)"},
        {"id": "deepseek-r1:14b", "name": "DeepSeek R1 (14B)"},
    ]
    return jsonify(models)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
