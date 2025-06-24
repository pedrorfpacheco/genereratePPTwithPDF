# tests/test_pdf_extractor.py
from unittest.mock import patch, MagicMock

import pytest

from readPDF import PdfExtractor


class TestPdfExtractor:

    @patch('readPDF.PyPDF2.PdfReader')
    def test_extract_with_pypdf2(self, mock_pdf_reader):
        # Configurar o mock do PdfReader
        mock_reader = MagicMock()
        mock_pdf_reader.return_value = mock_reader

        # Configurar páginas mock
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Texto da página"
        mock_reader.pages = [mock_page, mock_page]  # Simula duas páginas

        # Patch para abrir arquivo que não existe
        with patch('builtins.open', MagicMock()):
            result = PdfExtractor.extract_with_pypdf2("teste.pdf")

        # Verificar resultado
        assert "Texto da página" in result
        assert mock_page.extract_text.call_count == 2

    @patch('readPDF.pdfminer_extract_text')
    def test_extract_with_pdfminer(self, mock_extract_text):
        # Configurar o mock do pdfminer_extract_text
        mock_extract_text.return_value = "Texto extraído com PDFMiner"

        # Chamar a função
        result = PdfExtractor.extract_with_pdfminer("teste.pdf")

        # Verificações
        assert result == "Texto extraído com PDFMiner"
        mock_extract_text.assert_called_once()

    @patch('readPDF.PdfExtractor.extract_with_pypdf2')
    @patch('readPDF.PdfExtractor.extract_with_pdfminer')
    def test_extract_text_success(self, mock_pdfminer, mock_pypdf2):
        # Configurar resultados dos mocks
        mock_pypdf2.return_value = "Texto PyPDF2 mais curto"
        mock_pdfminer.return_value = "Texto PDFMiner com conteúdo bem mais extenso"

        # Testar a função principal
        result = PdfExtractor.extract_text("arquivo_teste.pdf")

        # Deve escolher o texto mais longo (PDFMiner neste caso)
        assert result == "Texto PDFMiner com conteúdo bem mais extenso"
        mock_pypdf2.assert_called_once_with("arquivo_teste.pdf")
        mock_pdfminer.assert_called_once_with("arquivo_teste.pdf")

    @patch('readPDF.PdfExtractor.extract_with_pypdf2')
    @patch('readPDF.PdfExtractor.extract_with_pdfminer')
    def test_extract_text_fallback_to_pypdf2(self, mock_pdfminer, mock_pypdf2):
        # Simular falha no PDFMiner
        mock_pdfminer.return_value = None
        mock_pypdf2.return_value = "Texto de fallback do PyPDF2"

        result = PdfExtractor.extract_text("arquivo_teste.pdf")

        # Deve usar PyPDF2 como fallback
        assert result == "Texto de fallback do PyPDF2"

    @patch('readPDF.PdfExtractor.extract_with_pypdf2')
    @patch('readPDF.PdfExtractor.extract_with_pdfminer')
    def test_extract_text_all_methods_fail(self, mock_pdfminer, mock_pypdf2):
        # Simular falha em ambos os métodos
        mock_pdfminer.return_value = None
        mock_pypdf2.return_value = None

        # Deve lançar exceção quando todos os métodos falham
        with pytest.raises(Exception) as excinfo:
            PdfExtractor.extract_text("arquivo_inexistente.pdf")

        assert "Could not extract text from PDF using any method" in str(excinfo.value)

    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        # Criar um arquivo de teste vazio
        pdf_path = tmp_path / "sample.pdf"
        pdf_path.write_bytes(b"%PDF-1.5\n")  # Cabeçalho PDF mínimo
        return str(pdf_path)

    def test_integration_with_sample_file(self, sample_pdf_path):
        # Este teste só será executado se os mocks acima não interferirem
        with patch('readPDF.PdfExtractor.extract_with_pypdf2', return_value="Texto extraído"):
            with patch('readPDF.PdfExtractor.extract_with_pdfminer', return_value=None):
                result = PdfExtractor.extract_text(sample_pdf_path)
                assert result == "Texto extraído"