# tests/test_main.py
import os
from unittest.mock import patch, MagicMock

from main import pdf_to_pptx_with_ollama, normalize_document_structure, create_fallback_structure


class TestMainFunctions:

    @patch('main.OllamaProcessor')
    @patch('main.PdfExtractor')
    @patch('main.PdfToPptxConverter')
    @patch('image_extractor.ImageExtractor.extract_images_from_pdf')
    def test_pdf_to_pptx_with_ollama(self, mock_extract_images, mock_converter_class,
                                     mock_extractor_class, mock_processor_class, sample_pdf_path, temp_dir):
        # Configure mocks
        mock_extractor = MagicMock()
        mock_extractor.extract_text.return_value = "Extracted text from PDF"
        mock_extractor_class.return_value = mock_extractor

        mock_processor = MagicMock()
        mock_processor.clean_and_structure_text.return_value = "Cleaned text"
        mock_processor.analyze_document_with_images.return_value = {
            "title": "Document",
            "sections": [{"title": "Section 1", "content": ["Content 1"]}]
        }
        mock_processor_class.return_value = mock_processor

        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter

        mock_extract_images.return_value = [{"path": "image1.jpg", "page_num": 0}]

        # Execute the function
        output_file = os.path.join(temp_dir, "output.pptx")
        result = pdf_to_pptx_with_ollama(pdf_path=sample_pdf_path, output_file=output_file)

        # Assertions
        assert result == output_file
        mock_extractor.extract_text.assert_called_once_with(sample_pdf_path)
        mock_processor.clean_and_structure_text.assert_called_once()
        mock_processor.analyze_document_with_images.assert_called_once()
        mock_converter.create_presentation.assert_called_once()

    def test_normalize_document_structure(self):
        # Case 1: Structure is already a valid dictionary
        valid_structure = {
            "title": "Document",
            "sections": [{"title": "Section 1", "content": ["Content 1"]}]
        }
        result = normalize_document_structure(valid_structure, "Document Name", "Original text")
        assert result["title"] == "Document"
        assert len(result["sections"]) == 1

        # Case 2: Structure is a valid JSON string
        json_structure = '{"title": "JSON Document", "sections": [{"title": "JSON Section", "content": ["Item 1"]}]}'
        result = normalize_document_structure(json_structure, "Document Name", "Original text")
        assert result["title"] == "JSON Document"

        # Case 3: Invalid structure, fallback created
        with patch('main.create_fallback_structure') as mock_fallback:
            mock_fallback.return_value = {"title": "Fallback", "sections": []}
            result = normalize_document_structure(None, "Document Name", "Original text")
            mock_fallback.assert_called_once()
            assert result["title"] == "Fallback"

    def test_create_fallback_structure(self):
        text = "# Title 1\nContent of title 1\n\n# Title 2\nContent of title 2"
        document_name = "Test Document"

        result = create_fallback_structure(text, document_name)

        assert result["title"] == document_name
        assert len(result["sections"]) > 0