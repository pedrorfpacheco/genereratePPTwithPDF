import os
import time
import threading

from flask import Flask, render_template, request, send_file, jsonify, after_this_request
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
    ollama_processor = OllamaProcessor(model_name=model_name)

    if not output_file:
        if pdf_path:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_file = f"{base_name}.pptx"
        else:
            output_file = "presentation.pptx"

    text = pdf_text
    document_name = None

    if not text and pdf_path:
        print(f"Extracting text from PDF: {pdf_path}")
        extractor = PdfExtractor()
        text = extractor.extract_text(pdf_path)
        document_name = os.path.splitext(os.path.basename(pdf_path))[0]

    if not text:
        raise ValueError("No text provided or extracted from PDF")

    print("Cleaning and structuring text with Ollama...")
    cleaned_text = ollama_processor.clean_and_structure_text(text)

    print("Analyzing document structure with Ollama...")
    document_structure = ollama_processor.analyze_document_structure(cleaned_text)

    if isinstance(document_structure, str):
        try:
            import json
            document_structure = json.loads(document_structure)
        except json.JSONDecodeError:
            content_text = document_structure

            document_structure = {
                "title": "Document",
                "subtitle": "",
                "sections": []
            }

            lines = content_text.split('\n')
            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('#'):
                    if not document_structure["title"]:
                        document_structure["title"] = line.lstrip('#').strip()
                    else:
                        current_section = {
                            "title": line.lstrip('#').strip(),
                            "content": []
                        }
                        document_structure["sections"].append(current_section)
                elif current_section:
                    current_section["content"].append(line)

    print(f"Generating PowerPoint presentation with {theme} theme...")
    converter = PdfToPptxConverter(output_file, ollama_processor, theme=theme)
    converter.create_presentation(document_structure)

    return output_file

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