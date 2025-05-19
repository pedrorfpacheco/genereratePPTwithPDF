import os
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename

# Importar a função principal do código existente
from manageData import OllamaProcessor
from ppt_generator import PdfToPptxConverter
from readPDF import PdfExtractor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limitar uploads a 16MB
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Criar a pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def pdf_to_pptx_with_ollama(pdf_path=None, pdf_text=None, output_file=None, model_name="llama3"):
    """
    Converte um arquivo PDF em uma apresentação PowerPoint usando Ollama para processamento

    Args:
        pdf_path (str, optional): Caminho para o arquivo PDF
        pdf_text (str, optional): Texto já extraído do PDF
        output_file (str, optional): Nome do arquivo de saída
        model_name (str): Nome do modelo Ollama a ser usado

    Returns:
        str: Caminho para o arquivo de saída
    """
    # Inicializar o processador Ollama
    ollama_processor = OllamaProcessor(model_name=model_name)

    # Definir nome do arquivo de saída se não fornecido
    if not output_file:
        if pdf_path:
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_file = f"{base_name}.pptx"
        else:
            output_file = "presentation.pptx"

    # Extrair texto do PDF se não foi fornecido
    text = pdf_text
    document_name = None

    if not text and pdf_path:
        print(f"Extraindo texto do PDF: {pdf_path}")
        extractor = PdfExtractor()
        text = extractor.extract_text(pdf_path)
        document_name = os.path.splitext(os.path.basename(pdf_path))[0]

    if not text:
        raise ValueError("Nenhum texto fornecido ou extraído do PDF")

    print("Limpando e estruturando o texto com Ollama...")
    cleaned_text = ollama_processor.clean_and_structure_text(text)

    print("Analisando a estrutura do documento com Ollama...")
    document_structure = ollama_processor.analyze_document_structure(cleaned_text)

    # Criar e salvar a apresentação
    print("Gerando apresentação PowerPoint...")
    converter = PdfToPptxConverter(output_file, ollama_processor)
    converter.create_presentation(document_structure)

    return output_file


def pdf_bytes_to_pptx(pdf_bytes, output_file="presentation.pptx", model_name="llama3"):
    """
    Converte bytes de um PDF em uma apresentação PowerPoint

    Args:
        pdf_bytes (bytes): Conteúdo do PDF em bytes
        output_file (str): Nome do arquivo de saída
        model_name (str): Nome do modelo Ollama a ser usado

    Returns:
        str: Caminho para o arquivo de saída
    """
    # Salvar temporariamente os bytes em um arquivo
    temp_pdf_path = "temp_pdf_file.pdf"
    with open(temp_pdf_path, "wb") as f:
        f.write(pdf_bytes)

    try:
        # Processar o PDF
        result = pdf_to_pptx_with_ollama(pdf_path=temp_pdf_path, output_file=output_file, model_name=model_name)
        return result
    finally:
        # Limpar o arquivo temporário
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)


@app.route('/')
def index():
    """Renderiza a página inicial"""
    return render_template('index.html')


@app.route('/convert', methods=['POST'])
def convert_pdf():
    """Processa o arquivo PDF enviado pelo usuário"""
    # Verificar se o arquivo foi enviado
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    file = request.files['pdf_file']

    # Verificar se o nome do arquivo é vazio
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    # Verificar se o arquivo é um PDF
    if file and allowed_file(file.filename):
        # Obter o modelo selecionado
        model_name = request.form.get('model', 'llama3')

        # Salvar o arquivo temporariamente
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Processar o arquivo
        try:
            # Ler o arquivo como bytes
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()

            # Nome para o arquivo de saída (mantendo o nome original)
            output_filename = os.path.splitext(filename)[0] + '.pptx'
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

            # Converter o PDF para PPTX
            pdf_bytes_to_pptx(pdf_bytes, output_file=output_path, model_name=model_name)

            # Retornar o arquivo para download
            return send_file(output_path,
                             as_attachment=True,
                             download_name=output_filename,
                             mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')

        except Exception as e:
            # Em caso de erro, limpar arquivos temporários
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except PermissionError:
                    pass  # Ignorar erro se arquivo estiver em uso
            return jsonify({'error': f'Erro ao processar o arquivo: {str(e)}'}), 500

        finally:
            # Limpar apenas o arquivo PDF temporário
            # O arquivo PPTX será mantido para download e removido posteriormente
            if os.path.exists(file_path):
                os.remove(file_path)

    else:
        return jsonify({'error': 'Tipo de arquivo não permitido. Por favor, envie um PDF.'}), 400


@app.route('/models')
def get_models():
    """Retorna a lista de modelos disponíveis para o usuário escolher"""
    # Lista de modelos Ollama - ajuste conforme necessário
    models = [
        {"id": "llama3.2:1b", "name": "Llama 3.2 (1B)"},
        {"id": "deepseek-r1:14b", "name": "DeepSeek R1 (14B)"},
    ]
    return jsonify(models)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)