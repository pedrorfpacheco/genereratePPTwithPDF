import os

from flask import Flask, jsonify, request, render_template_string, send_file

from ppt_generator import PresentationGenerator
from readPDF import PDFProcessor

app = Flask(__name__)

# HTML template with file upload form and download button
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Procedure Summary Generator</title>
    <style>
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .summary { margin-top: 20px; padding: 10px; background-color: #f5f5f5; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Upload Procedural Resource (PDF)</h2>
        <form action="/process" method="POST" enctype="multipart/form-data">
            <input type="file" name="file" accept=".pdf" required>
            <input type="submit" value="Process and Generate Presentation">
        </form>
        {% if download_ready %}
            <div class="summary">
                <h3>Summary Generated!</h3>
                <p>{{ summary }}</p>
                <a href="/download" class="button">Download Presentation</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file and file.filename.endswith('.pdf'):
        try:
            # Process PDF and extract text
            pdf_processor = PDFProcessor(file)
            extracted_text = pdf_processor.extract_text()

            # Generate presentation with extracted text
            ppt_generator = PresentationGenerator(file)
            ppt_generator.create_presentation_with_text(extracted_text)

            return render_template_string(
                HTML_TEMPLATE,
                download_ready=True,
                summary=extracted_text[:500]  # Display a preview of the extracted text
            )
        except Exception as e:
            return jsonify({"error": f"Error processing file: {str(e)}"})
    else:
        return jsonify({"error": "Please upload a PDF file"})

@app.route('/download')
def download():
    try:
        return send_file(
            'output/presentation.pptx',
            as_attachment=True,
            download_name='extracted_text_presentation.pptx'
        )
    except Exception as e:
        return jsonify({"error": "Error downloading file"})

if __name__ == '__main__':
    os.makedirs('output', exist_ok=True)
    app.run()