# tests/test_ppt_generator.py
from unittest.mock import patch, MagicMock

from ppt_generator import PdfToPptxConverter


class TestPdfToPptxConverter:

    def test_init(self):
        converter = PdfToPptxConverter("test.pptx", theme="corporate")
        assert converter.output_filename == "test.pptx"
        assert converter.theme == "corporate"
        assert hasattr(converter, "title_color")

    @patch('pptx.Presentation')
    def test_add_title_slide(self, mock_presentation_class):
        # Configure mocks
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

        # Create the converter and call the method
        converter = PdfToPptxConverter()
        converter.prs = mock_presentation

        result = converter._add_title_slide("Test Title", "Subtitle")

        # Verify if the method was called correctly
        mock_slides.add_slide.assert_called_once()
        assert mock_title_shape.text == "Test Title"