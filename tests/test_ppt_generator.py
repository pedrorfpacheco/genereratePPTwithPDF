# tests/test_ppt_generator.py
import pytest
from unittest.mock import patch, MagicMock
import os
from ppt_generator import PdfToPptxConverter


class TestPdfToPptxConverter:

    def test_init(self):
        converter = PdfToPptxConverter("test.pptx", theme="corporate")
        assert converter.output_filename == "test.pptx"
        assert converter.theme == "corporate"
        assert hasattr(converter, "title_color")

    @patch('pptx.Presentation')
    def test_add_title_slide(self, mock_presentation_class):
        # Configurar mocks
        mock_presentation = MagicMock()
        mock_presentation_class.return_value = mock_presentation

        mock_slide = MagicMock()
        mock_slides = MagicMock()
        mock_slides.add_slide.return_value = mock_slide
        mock_presentation.slides = mock_slides

        mock_slide_layouts = MagicMock()
        mock_presentation.slide_layouts = [mock_slide_layouts]

        mock_title_shape = MagicMock()
        mock_slide.shapes.title = mock_title_shape

        mock_placeholders = [MagicMock(), MagicMock()]
        mock_slide.placeholders = mock_placeholders

        # Criar o conversor e chamar o método
        converter = PdfToPptxConverter()
        converter.prs = mock_presentation

        result = converter._add_title_slide("Título de Teste", "Subtítulo")

        # Verificar se o método foi chamado corretamente
        mock_slides.add_slide.assert_called_once()
        assert mock_title_shape.text == "Título de Teste"
