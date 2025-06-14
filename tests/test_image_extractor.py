# tests/test_image_extractor.py
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from image_extractor import ImageExtractor


class TestImageExtractor:
    # tests/test_image_extractor.py
    import pytest
    import os
    import tempfile
    from image_extractor import ImageExtractor

    class TestImageExtractor:

        def test_extract_images_from_pdf_with_valid_pdf(self, sample_pdf_path):
            """Testa a extração de imagens de um PDF válido."""
            with tempfile.TemporaryDirectory() as temp_dir:
                result = ImageExtractor.extract_images_from_pdf(sample_pdf_path, temp_dir)

                # Verifica se o resultado é uma lista
                assert isinstance(result, list)

                # Se o PDF de teste contém imagens, verifica se foram extraídas corretamente
                if result:
                    assert "path" in result[0]
                    assert "page_num" in result[0]
                    assert "width" in result[0]
                    assert "height" in result[0]
                    assert "size" in result[0]
                    assert os.path.exists(result[0]["path"])

    @patch('fitz.open')
    def test_extract_images_with_mock(self, mock_fitz_open):
        """Testa a extração de imagens com valores simulados."""
        # Configurar os mocks
        mock_pdf = MagicMock()
        mock_page = MagicMock()
        mock_pdf.__iter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_pdf

        # Configurar o mock para a extração de imagens
        mock_img_list = [(1, (0, 0, 0, 0, 0, 0, 0))]
        mock_page.get_images.return_value = mock_img_list

        # Configurar o mock para a imagem extraída
        mock_pdf.extract_image.return_value = {
            "image": b"imagem_simulada",
            "ext": "jpg"
        }

        # Patch para Image.open
        with patch('PIL.Image.open') as mock_pil_open:
            mock_image = MagicMock()
            mock_image.size = (800, 600)
            mock_pil_open.return_value = mock_image

            # Patch para o open() do Python
            with patch('builtins.open', MagicMock()):
                result = ImageExtractor.extract_images_from_pdf("caminho_ficticio.pdf")

                # Verificações
                assert len(result) == 1
                assert result[0]["page_num"] == 0
                assert result[0]["width"] == 800
                assert result[0]["height"] == 600

    def test_extract_images_empty_pdf(self):
        """Testa extração de um PDF sem imagens (simulado)."""
        with patch('fitz.open') as mock_fitz_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_page.get_images.return_value = []  # Sem imagens
            mock_pdf.__iter__.return_value = [mock_page]
            mock_fitz_open.return_value = mock_pdf

            result = ImageExtractor.extract_images_from_pdf("sem_imagens.pdf")

            assert result == []

    def test_filter_small_images(self):
        """Testa se imagens pequenas são filtradas corretamente."""
        with patch('fitz.open') as mock_fitz_open, \
                patch('PIL.Image.open') as mock_pil_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_pdf.__iter__.return_value = [mock_page]
            mock_fitz_open.return_value = mock_pdf

            # Imagem pequena: 100x100 pixels
            mock_img_list = [(1, (0, 0, 0, 0, 0, 0, 0))]
            mock_page.get_images.return_value = mock_img_list

            mock_pdf.extract_image.return_value = {
                "image": b"imagem_pequena",
                "ext": "jpg"
            }

            mock_image = MagicMock()
            mock_image.size = (100, 100)  # Dimensão menor que o limite (150x150)
            mock_pil_open.return_value = mock_image

            with patch('builtins.open', MagicMock()):
                result = ImageExtractor.extract_images_from_pdf("pdf_com_imagens_pequenas.pdf")

                # A imagem deve ser filtrada por ser pequena
                assert result == []

    def test_error_handling(self):
        """Testa manipulação de erros durante a extração."""
        with patch('fitz.open') as mock_fitz_open:
            mock_fitz_open.side_effect = Exception("Erro simulado")

            result = ImageExtractor.extract_images_from_pdf("arquivo_com_erro.pdf")

            # Se ocorrer um erro, o método deve retornar uma lista vazia
            assert result == []

    @pytest.fixture
    def mock_pdf_with_image(self):
        """Fixture que cria um mock de PDF com uma imagem."""
        with patch('fitz.open') as mock_fitz_open:
            mock_pdf = MagicMock()
            mock_page = MagicMock()
            mock_pdf.__iter__.return_value = [mock_page]
            mock_fitz_open.return_value = mock_pdf

            mock_img_list = [(1, (0, 0, 0, 0, 0, 0, 0))]
            mock_page.get_images.return_value = mock_img_list

            mock_pdf.extract_image.return_value = {
                "image": b"dados_da_imagem",
                "ext": "jpg"
            }

            yield mock_fitz_open, mock_pdf, mock_page