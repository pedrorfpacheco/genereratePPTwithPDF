import pypdf
from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt

from manageData import TextManager


class PresentationGenerator:
    def __init__(self, file_obj):
        self.prs = Presentation()
        self.title_slide_layout = self.prs.slide_layouts[0]
        self.content_slide_layout = self.prs.slide_layouts[1]
        self.reader = pypdf.PdfReader(file_obj)

    def create_presentation_with_text(self, text: str) -> None:
        """Create a PowerPoint presentation with a single slide containing the extracted text."""
        #text_manager = TextManager(text)
        #extracted_sentences = text_manager.extract_sentences(text)
        #preprocessed_text = text_manager.preprocess_text(text)
        #clusters = text_manager.cluster_sentences(extracted_sentences)

        # Create title slide
        self._create_title_slide(text)

        # Create content slide with extracted text
        self._create_content_slide(text)

        # Save the presentation
        self.prs.save('output/presentation.pptx')

    def _create_title_slide(self, text: str) -> None:
        """Create the title slide."""
        slide = self.prs.slides.add_slide(self.title_slide_layout)
        title_shape = slide.shapes.title
        subtitle_shape = slide.placeholders[1]

        text_manager = TextManager(text)
        title = text_manager.extract_document_title()
        subtitle = text_manager.extract_document_subtitle()
        author = text_manager.extract_author()

        title_shape.text = title
        subtitle_shape.text = subtitle
        author_shape = slide.shapes.add_textbox(1, 3, 8, 1)
        text_frame = author_shape.text_frame
        text_frame.text = f"Author: {author}"

    def _create_content_slide(self, text: str) -> None:
        """Create a slide with the extracted text."""
        slide = self.prs.slides.add_slide(self.content_slide_layout)
        title_shape = slide.shapes.title
        content_shape = slide.placeholders[1]

        text_first_page = 'Hello my friend, I love you so much. TJI is very good employee and manager. I will go to somny festival this year'
        text_manager = TextManager(text)

        title_shape.text = "Extracted Text"
        text_frame = content_shape.text_frame
        text_frame.clear()
        p = text_frame.add_paragraph()
        p.text = text_manager.summarize_text(text_first_page)
        p.font.size = Pt(14)
        p.alignment = PP_ALIGN.LEFT