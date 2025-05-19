import re
import os
import json
import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdfminer.layout import LAParams
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
import ollama  # Importando a biblioteca Ollama

class PdfExtractor:
    """Classe para extrair texto de documentos PDF usando múltiplos métodos"""

    @staticmethod
    def extract_with_pypdf2(pdf_path):
        """Extrai texto usando PyPDF2"""
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
            print(f"Erro ao extrair texto com PyPDF2: {e}")
            return None

    @staticmethod
    def extract_with_pdfminer(pdf_path):
        """Extrai texto usando PDFMiner"""
        try:
            laparams = LAParams(line_margin=0.5, char_margin=2.0, all_texts=True)
            text = pdfminer_extract_text(pdf_path, laparams=laparams)
            return text
        except Exception as e:
            print(f"Erro ao extrair texto com PDFMiner: {e}")
            return None

    @staticmethod
    def extract_text(pdf_path):
        """Tenta extrair texto usando múltiplas bibliotecas e retorna o melhor resultado"""
        # Primeiro tentamos com PyPDF2
        text_pypdf2 = PdfExtractor.extract_with_pypdf2(pdf_path)

        # Depois com PDFMiner
        text_pdfminer = PdfExtractor.extract_with_pdfminer(pdf_path)

        # Escolhe o melhor resultado (o que tiver mais conteúdo)
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
            raise Exception("Não foi possível extrair texto do PDF com nenhum método")


