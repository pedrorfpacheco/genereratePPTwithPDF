# tests/test_main.py
import pytest
from unittest.mock import patch, MagicMock
import os
import io
from main import pdf_to_pptx_with_ollama, normalize_document_structure, create_fallback_structure


class TestMainFunctions:

    @patch('main.OllamaProcessor')
    @patch('main.PdfExtractor')
    @patch('main.PdfToPptxConverter')
    @patch('image_extractor.ImageExtractor.extract_images_from_pdf')
    def test_pdf_to_pptx_with_ollama(self, mock_extract_images, mock_converter_class,
                                     mock_extractor_class, mock_processor_class, sample_pdf_path, temp_dir):
        # Configurar mocks
        mock_extractor = MagicMock()
        mock_extractor.extract_text.return_value = "Texto extraído do PDF"
        mock_extractor_class.return_value = mock_extractor

        mock_processor = MagicMock()
        mock_processor.clean_and_structure_text.return_value = "Texto limpo"
        mock_processor.analyze_document_with_images.return_value = {
            "title": "Documento",
            "sections": [{"title": "Seção 1", "content": ["Conteúdo 1"]}]
        }
        mock_processor_class.return_value = mock_processor

        mock_converter = MagicMock()
        mock_converter_class.return_value = mock_converter

        mock_extract_images.return_value = [{"path": "imagem1.jpg", "page_num": 0}]

        # Executar a função
        output_file = os.path.join(temp_dir, "output.pptx")
        result = pdf_to_pptx_with_ollama(pdf_path=sample_pdf_path, output_file=output_file)

        # Verificações
        assert result == output_file
        mock_extractor.extract_text.assert_called_once_with(sample_pdf_path)
        mock_processor.clean_and_structure_text.assert_called_once()
        mock_processor.analyze_document_with_images.assert_called_once()
        mock_converter.create_presentation.assert_called_once()

    def test_normalize_document_structure(self):
        # Caso 1: Estrutura já é dicionário válido
        valid_structure = {
            "title": "Documento",
            "sections": [{"title": "Seção 1", "content": ["Conteúdo 1"]}]
        }
        result = normalize_document_structure(valid_structure, "Nome do Documento", "Texto original")
        assert result["title"] == "Documento"
        assert len(result["sections"]) == 1

        # Caso 2: Estrutura é string JSON válida
        json_structure = '{"title": "Documento JSON", "sections": [{"title": "Seção JSON", "content": ["Item 1"]}]}'
        result = normalize_document_structure(json_structure, "Nome do Documento", "Texto original")
        assert result["title"] == "Documento JSON"

        # Caso 3: Estrutura inválida, fallback criado
        with patch('main.create_fallback_structure') as mock_fallback:
            mock_fallback.return_value = {"title": "Fallback", "sections": []}
            result = normalize_document_structure(None, "Nome do Documento", "Texto original")
            mock_fallback.assert_called_once()
            assert result["title"] == "Fallback"

    def test_create_fallback_structure(self):
        text = "# Título 1\nConteúdo do título 1\n\n# Título 2\nConteúdo do título 2"
        document_name = "Documento de Teste"

        result = create_fallback_structure(text, document_name)

        assert result["title"] == document_name
        assert len(result["sections"]) > 0