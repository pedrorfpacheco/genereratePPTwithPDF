# tests/test_ollama_processor.py
import pytest
from unittest.mock import patch, MagicMock
from manageData import OllamaProcessor


class TestOllamaProcessor:

    @patch('manageData.ollama.chat')
    def test_clean_and_structure_text(self, mock_ollama_chat):
        # Configurar o mock
        mock_response = {
            'message': {'content': 'Texto limpo e estruturado'}
        }
        mock_ollama_chat.return_value = mock_response

        processor = OllamaProcessor(model_name="test_model")
        result = processor.clean_and_structure_text("Texto original")

        # Verificar se o ollama.chat foi chamado corretamente
        mock_ollama_chat.assert_called_once()
        assert "Texto original" in mock_ollama_chat.call_args[1]['messages'][0]['content']
        assert result == "Texto limpo e estruturado"

    @patch('manageData.ollama.chat')
    def test_analyze_document_structure(self, mock_ollama_chat):
        mock_response = {
            'message': {
                'content': '```json\n{"title": "Documento","sections": [{"title": "Seção 1","content": ["Item 1"]}]}\n```'}
        }
        mock_ollama_chat.return_value = mock_response

        processor = OllamaProcessor()
        result = processor.analyze_document_structure("Texto do documento")

        assert result["title"] == "Documento"
        assert len(result["sections"]) == 1
        assert result["sections"][0]["title"] == "Seção 1"

    @patch('manageData.ollama.chat')
    def test_analyze_document_with_images(self, mock_ollama_chat):
        # Mock para analyze_document_structure
        processor = OllamaProcessor()
        processor.analyze_document_structure = MagicMock(return_value={
            "title": "Documento",
            "sections": [{"title": "Seção 1", "content": ["Item 1"]}]
        })

        # Mock para a chamada ollama.chat no método analyze_document_with_images
        mock_response = {
            'message': {
                'content': '```json\n{"sections": [{"title": "Seção 1","relevant_images": [0],"presentation_style": "side-by-side"}]}\n```'}
        }
        mock_ollama_chat.return_value = mock_response

        # Dados de teste
        image_data = [{"path": "imagem1.jpg", "page_num": 0, "width": 800, "height": 600}]

        # Chamar o método sob teste
        result = processor.analyze_document_with_images("Texto do documento", image_data)

        # Verificações
        assert "sections" in result
        assert result["sections"][0]["has_images"] is True
        assert "image_info" in result["sections"][0]
        assert result["sections"][0]["image_info"]["relevant_images"] == [0]