import os

from manageData import OllamaProcessor
from ppt_generator import PdfToPptxConverter
from readPDF import PdfExtractor


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


# Exemplo de uso:
if __name__ == "__main__":
    # Exemplo 1: A partir de um arquivo PDF
    # pdf_to_pptx_with_ollama("documento_procedural.pdf", model_name="llama3")

    # Exemplo 2: A partir de texto já extraído

    sample_text = """Bosch Rexroth Canada Corp. reserves the right to revise t his information at any time and for 
any reason and reserves the right to make changes at a ny time, without notice or obligation, 
to any of the information contained in this piece of  literature. 
Please check for updates at: www.boschrexroth.ca/compu -spread 

3/16 
Bosch Rexroth Canada ı 11.25.2014 ı Revision 4.0  
1     System Components 
4/16 
Bosch Rexroth Canada ı 11.25.2014 ı Revision 4.0  
2     Spreader System Layout 
See Appendix See Appendix See Appendix See Appendix    (CS (CS (CS (CS-- --550 System Layout Drawing) 550 System Layout Drawing) 550 System Layout Drawing) 550 System Layout Drawing). . ..    
3     Joystick System Layout  
See Appen See Appen See Appen See Appendix dix dix dix    (CS550 (CS550 (CS550 (CS550-- --150RC System Layout Drawing) 150RC System Layout Drawing) 150RC System Layout Drawing) 150RC System Layout Drawing). . ..    
The following is a detailed navigation chart for the system layout. See Appendix for 
the detailed system layout including all the compone nts and part numbers.   
CS-550 / 150 ELECTRONIC SYSTEM BUILDER 
TABLE OF CONTENTS 
COORDINATES 
ITEM DESCRIPTION X.Y DETA ILS 
550 SPREADER 
1 SPREADER PACKAGES E1 DISPLAY AND RC INCLUDED 
2 MAIN HARNESS D7 ADVANCED OR LITE 
3 CANBUS CABLES C2 
4 SENSOR EXTENSIONS B6 
5 SENSOR NETWORK C6 PULL-UP RESISTOR (WHITE MOTOR) 
6 VEHICLE SPEED B7 
7 VALVE EX TENSIONS E6 IF RC LOCATED IN CAB 
8 550 AUX ILIARY CABLE E3 MATERIAL DETECT / CHANGE 
9 VALVE ADAPTER E6 (C4M TO ITT) FOR OLD SCB/MP18 
150 ARMREST 
1 RCE CABLES A3 IN-VALVE OR IN-CAB 
2 POWER FLOAT C4 NO ADAPTERS FOR NEW C4 BLOCK 
3 150 AUXILIARY B2 
4 CANBUS CABLE C2 
5 LOW OIL, SPIN. REV. C3 ADAPTERS REQUIRED 
SPECIAL FUNCTIONS 
1 PRESSURE/TEMP/CHUTE D3 HYDRAULIC MONITORING 
2 ROAD TEMP D0 ROAD AND AMBIENT TEMP 
3 WIFI D2 NEED EX TENSION? 
4 GPS PUCK E0 
5 ANTI-ICE E4 USE C4-C4 EXTENSIONS (CUT END) 
TOW PLOW 
1 TP SPREADER PKG E1 INCLUDES TWO 4-4's 
2 MAIN HARNESS D9 
3 CANBUS SPLITTER D6 
4 SENSOR EXTENSIONS B6 RC ON TRUCK OR TRAILER? 
5 SENSOR NETWORK C6 IF PULL-UP RESISTORS REQUIRED 
6 VALVE EX TENSIONS E6 RC ON TRUCK OR TRAILER? 
5/16 
Bosch Rexroth Canada ı 11.25.2014 ı Revision 4.0  
4     Mounting  
4.1    Microcontroller 
1.  The microcontrollers(s) can be mounted horizontal o r with the connectors 
oriented to the bottom. The controller cannot be mo unted with the connectors 
facing upwards. 
2.  The mounting surface must be flat and all four brack et holes used. 
3.  Sufficient space must be allowed for the mating and un-mating of the 
connectors. 
4.  If the controller is mounted in the cab, valve exte nsion cables are required to be 
routed into the valve enclosure. 
5.  If the controller is mounted in the valve enclosure , the main harness leads will 
terminate directly to the valve solenoid. 
6.  The mount hole spacing is 188mm (7.4") by 59mm (2.32 "). 
7.  See the "Installation Notes" for additional recomme ndations (page 15)."""

    pdf_to_pptx_with_ollama(pdf_text=sample_text, output_file="bosch_rexroth_system.pptx", model_name="llama3.2:1b")
