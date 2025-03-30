import pypdf

class PDFProcessor:
    def __init__(self, file_obj):
        self.reader = pypdf.PdfReader(file_obj)

    def extract_text(self) -> str:
        """Extract text from all pages of the PDF."""
        text = ""
        for page in self.reader.pages:
            text += page.extract_text() + "\n"
        return text

    def extract_first_page_text(self) -> str:
        """Extract text from the first page of the PDF."""
        return self.reader.pages[0].extract_text()

