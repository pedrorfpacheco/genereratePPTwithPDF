# tests/test_pdf_extractor.py
from unittest.mock import patch, MagicMock

import pytest

from readPDF import PdfExtractor


class TestPdfExtractor:

    @patch('readPDF.PyPDF2.PdfReader')
    def test_extract_with_pypdf2(self, mock_pdf_reader):
        # Configure the PdfReader mock
        mock_reader = MagicMock()
        mock_pdf_reader.return_value = mock_reader

        # Configure mock pages
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page text"
        mock_reader.pages = [mock_page, mock_page]  # Simulate two pages

        # Patch to open a non-existent file
        with patch('builtins.open', MagicMock()):
            result = PdfExtractor.extract_with_pypdf2("test.pdf")

        # Verify result
        assert "Page text" in result
        assert mock_page.extract_text.call_count == 2

    @patch('readPDF.pdfminer_extract_text')
    def test_extract_with_pdfminer(self, mock_extract_text):
        # Configure the pdfminer_extract_text mock
        mock_extract_text.return_value = "Text extracted with PDFMiner"

        # Call the function
        result = PdfExtractor.extract_with_pdfminer("test.pdf")

        # Assertions
        assert result == "Text extracted with PDFMiner"
        mock_extract_text.assert_called_once()

    @patch('readPDF.PdfExtractor.extract_with_pypdf2')
    @patch('readPDF.PdfExtractor.extract_with_pdfminer')
    def test_extract_text_success(self, mock_pdfminer, mock_pypdf2):
        # Configure mock results
        mock_pypdf2.return_value = "Shorter PyPDF2 text"
        mock_pdfminer.return_value = "Much longer PDFMiner text content"

        # Test the main function
        result = PdfExtractor.extract_text("test_file.pdf")

        # Should choose the longer text (PDFMiner in this case)
        assert result == "Much longer PDFMiner text content"
        mock_pypdf2.assert_called_once_with("test_file.pdf")
        mock_pdfminer.assert_called_once_with("test_file.pdf")

    @patch('readPDF.PdfExtractor.extract_with_pypdf2')
    @patch('readPDF.PdfExtractor.extract_with_pdfminer')
    def test_extract_text_fallback_to_pypdf2(self, mock_pdfminer, mock_pypdf2):
        # Simulate PDFMiner failure
        mock_pdfminer.return_value = None
        mock_pypdf2.return_value = "PyPDF2 fallback text"

        result = PdfExtractor.extract_text("test_file.pdf")

        # Should use PyPDF2 as fallback
        assert result == "PyPDF2 fallback text"

    @patch('readPDF.PdfExtractor.extract_with_pypdf2')
    @patch('readPDF.PdfExtractor.extract_with_pdfminer')
    def test_extract_text_all_methods_fail(self, mock_pdfminer, mock_pypdf2):
        # Simulate failure in both methods
        mock_pdfminer.return_value = None
        mock_pypdf2.return_value = None

        # Should raise an exception when all methods fail
        with pytest.raises(Exception) as excinfo:
            PdfExtractor.extract_text("non_existent_file.pdf")

        assert "Could not extract text from PDF using any method" in str(excinfo.value)

    @pytest.fixture
    def sample_pdf_path(self, tmp_path):
        # Create an empty test file
        pdf_path = tmp_path / "sample.pdf"
        pdf_path.write_bytes(b"%PDF-1.5\n")  # Minimal PDF header
        return str(pdf_path)

    def test_integration_with_sample_file(self, sample_pdf_path):
        # This test will only run if the above mocks do not interfere
        with patch('readPDF.PdfExtractor.extract_with_pypdf2', return_value="Extracted text"):
            with patch('readPDF.PdfExtractor.extract_with_pdfminer', return_value=None):
                result = PdfExtractor.extract_text(sample_pdf_path)
                assert result == "Extracted text"