# tests/test_image_extractor.py
import os
import tempfile
from unittest.mock import patch, MagicMock

from image_extractor import ImageExtractor


class TestImageExtractor:
    # tests/test_image_extractor.py
    import pytest

    class TestImageExtractor:

        def test_extract_images_from_pdf_with_valid_pdf(self, sample_pdf_path):
            """Tests image extraction from a valid PDF."""
            with tempfile.TemporaryDirectory() as temp_dir:
                result = ImageExtractor.extract_images_from_pdf(sample_pdf_path, temp_dir)

                # Checks if the result is a list
                assert isinstance(result, list)

                # If the test PDF contains images, checks if they were extracted correctly
                if result:
                    assert "path" in result[0]
                    assert "page_num" in result[0]
                    assert "width" in result[0]
                    assert "height" in result[0]
                    assert "size" in result[0]
                    assert os.path.exists(result[0]["path"])

    @patch('fitz.open')
    def test_extract_images_with_mock(self, mock_fitz_open):
        """Tests image extraction with mocked values."""
        # Configure the mocks
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_pdf.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_pdf

        # Configure the mock for image extraction
        mock_img_list = [(1, (0, 0, 0, 0, 0, 0, 0))]
        mock_page.get_images.return_value = mock_img_list

        # Configure the mock for the extracted image
        mock_pdf.extract_image.return_value = {
            "image": b"mock_image",
            "ext": "jpg"
        }

        # Patch for Image.open
        with patch('PIL.Image.open') as mock_pil_open:
            mock_image = MagicMock()
            mock_image.size = (800, 600)
            mock_pil_open.return_value = mock_image

            # Patch for Python's open()
            with patch('builtins.open', MagicMock()):
                result = ImageExtractor.extract_images_from_pdf("fictitious_path.pdf")

                # Assertions
                assert len(result) == 1
                assert result[0]["page_num"] == 0
                assert result[0]["width"] == 800
                assert result[0]["height"] == 600

    def test_extract_images_empty_pdf(self):
        """Tests extraction from a PDF without images (mocked)."""
        with patch('fitz.open') as mock_fitz_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.get_images.return_value = []  # No images
            mock_pdf.__iter__.return_value = [mock_page]
            mock_fitz_open.return_value = mock_pdf

            result = ImageExtractor.extract_images_from_pdf("no_images.pdf")

            assert result == []

    def test_filter_small_images(self):
        """Tests if small images are filtered correctly."""
        with patch('fitz.open') as mock_fitz_open, \
                patch('PIL.Image.open') as mock_pil_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_pdf.__iter__.return_value = [mock_page]
            mock_fitz_open.return_value = mock_pdf

            # Small image: 100x100 pixels
            mock_img_list = [(1, (0, 0, 0, 0, 0, 0, 0))]
            mock_page.get_images.return_value = mock_img_list

            mock_pdf.extract_image.return_value = {
                "image": b"small_image_data",
                "ext": "jpg"
            }

            mock_image = MagicMock()
            mock_image.size = (100, 100)  # Dimension smaller than the limit (150x150)
            mock_pil_open.return_value = mock_image

            with patch('builtins.open', MagicMock()):
                result = ImageExtractor.extract_images_from_pdf("pdf_with_small_images.pdf")

                # The image should be filtered because it's small
                assert result == []

    def test_error_handling(self):
        """Tests error handling during extraction."""
        with patch('fitz.open') as mock_fitz_open:
            mock_fitz_open.side_effect = Exception("Simulated error")

            result = ImageExtractor.extract_images_from_pdf("error_file.pdf")

            # If an error occurs, the method should return an empty list
            assert result == []

    @pytest.fixture
    def mock_pdf_with_image(self):
        """Fixture that creates a PDF mock with an image."""
        with patch('fitz.open') as mock_fitz_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_pdf.__iter__.return_value = [mock_page]
            mock_fitz_open.return_value = mock_pdf

            mock_img_list = [(1, (0, 0, 0, 0, 0, 0, 0))]
            mock_page.get_images.return_value = mock_img_list

            mock_pdf.extract_image.return_value = {
                "image": b"image_data",
                "ext": "jpg"
            }

            yield mock_fitz_open, mock_pdf, mock_page