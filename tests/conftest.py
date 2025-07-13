# tests/conftest.py
import pytest
import os

@pytest.fixture
def sample_pdf_path():
    """Returns the path to a sample PDF file for testing."""
    # Adjust the path as needed
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "resources", "sample.pdf")

@pytest.fixture
def temp_dir(tmpdir):
    """Returns a temporary directory for testing."""
    return str(tmpdir)