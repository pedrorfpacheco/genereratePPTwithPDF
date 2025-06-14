# tests/conftest.py
import pytest
import os

@pytest.fixture
def sample_pdf_path():
    """Retorna o caminho para um arquivo PDF de amostra para testes."""
    # Ajuste o caminho conforme necessário
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "resources", "sample.pdf")

@pytest.fixture
def temp_dir(tmpdir):
    """Retorna um diretório temporário para testes."""
    return str(tmpdir)