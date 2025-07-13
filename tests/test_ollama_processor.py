# tests/test_ollama_processor.py
from unittest.mock import patch, MagicMock

from manageData import OllamaProcessor


class TestOllamaProcessor:

    @patch('manageData.ollama.chat')
    def test_clean_and_structure_text(self, mock_ollama_chat):
        # Configure the mock
        mock_response = {
            'message': {'content': 'Cleaned and structured text'}
        }
        mock_ollama_chat.return_value = mock_response

        processor = OllamaProcessor(model_name="test_model")
        result = processor.clean_and_structure_text("Original text")

        # Verify that ollama.chat was called correctly
        mock_ollama_chat.assert_called_once()
        assert "Original text" in mock_ollama_chat.call_args[1]['messages'][0]['content']
        assert result == "Cleaned and structured text"

    @patch('manageData.ollama.chat')
    def test_analyze_document_structure(self, mock_ollama_chat):
        mock_response = {
            'message': {
                'content': '```json\n{"title": "Document","sections": [{"title": "Section 1","content": ["Item 1"]}]}\n```'}
        }
        mock_ollama_chat.return_value = mock_response

        processor = OllamaProcessor()
        result = processor.analyze_document_structure("Document text")

        assert result["title"] == "Document"
        assert len(result["sections"]) == 1
        assert result["sections"][0]["title"] == "Section 1"

    @patch('manageData.ollama.chat')
    def test_analyze_document_with_images(self, mock_ollama_chat):
        # Mock for analyze_document_structure
        processor = OllamaProcessor()
        processor.analyze_document_structure = MagicMock(return_value={
            "title": "Document",
            "sections": [{"title": "Section 1", "content": ["Item 1"]}]
        })

        # Mock for the ollama.chat call in the analyze_document_with_images method
        mock_response = {
            'message': {
                'content': '```json\n{"sections": [{"title": "Section 1","relevant_images": [0],"presentation_style": "side-by-side"}]}\n```'}
        }
        mock_ollama_chat.return_value = mock_response

        # Test data
        image_data = [{"path": "image1.jpg", "page_num": 0, "width": 800, "height": 600}]

        # Call the method under test
        result = processor.analyze_document_with_images("Document text", image_data)

        # Assertions
        assert "sections" in result
        assert result["sections"][0]["has_images"] is True
        assert "image_info" in result["sections"][0]
        assert result["sections"][0]["image_info"]["relevant_images"] == [0]