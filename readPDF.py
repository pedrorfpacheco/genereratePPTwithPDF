import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdfminer.layout import LAParams


class PdfExtractor:

    @staticmethod
    def extract_with_pypdf2(pdf_path):
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                num_pages = len(reader.pages)

                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n\n"

            return text
        except Exception as e:
            print(f"Error extracting text with PyPDF2: {e}")
            return None

    @staticmethod
    def extract_with_pdfminer(pdf_path):
        try:
            laparams = LAParams(line_margin=0.5, char_margin=2.0, all_texts=True)
            text = pdfminer_extract_text(pdf_path, laparams=laparams)
            return text
        except Exception as e:
            print(f"Error extracting text with PDFMiner: {e}")
            return None

    @staticmethod
    def extract_text(pdf_path):
        text_pypdf2 = PdfExtractor.extract_with_pypdf2(pdf_path)

        text_pdfminer = PdfExtractor.extract_with_pdfminer(pdf_path)

        if text_pypdf2 and text_pdfminer:
            if len(text_pypdf2) > len(text_pdfminer):
                return text_pypdf2
            else:
                return text_pdfminer
        elif text_pypdf2:
            return text_pypdf2
        elif text_pdfminer:
            return text_pdfminer
        else:
            raise Exception("Could not extract text from PDF using any method")
