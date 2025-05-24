import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN


class PdfToPptxConverter:
    def __init__(self, output_filename="presentation.pptx", ollama_processor=None, theme="default"):
        self.prs = Presentation()
        self.output_filename = output_filename
        self.ollama_processor = ollama_processor
        self.theme = theme

        self.prs.slide_width = Inches(13.33)
        self.prs.slide_height = Inches(7.5)

        self.setup_theme_colors()

    def setup_theme_colors(self):
        if self.theme == "corporate":
            self.title_color = RGBColor(18, 52, 86)
            self.accent_color = RGBColor(64, 119, 176)
            self.text_color = RGBColor(50, 50, 50)
            self.background_color = RGBColor(242, 242, 242)
            self.title_font_size = Pt(36)
            self.subtitle_font_size = Pt(20)
            self.header_font_size = Pt(28)
            self.content_font_size = Pt(16)
        elif self.theme == "minimal":
            self.title_color = RGBColor(0, 0, 0)
            self.accent_color = RGBColor(204, 0, 0)
            self.text_color = RGBColor(40, 40, 40)
            self.background_color = RGBColor(255, 255, 255)
            self.title_font_size = Pt(38)
            self.subtitle_font_size = Pt(22)
            self.header_font_size = Pt(30)
            self.content_font_size = Pt(18)
        else:
            self.title_color = RGBColor(44, 86, 151)
            self.accent_color = RGBColor(0, 129, 198)
            self.text_color = RGBColor(68, 68, 68)
            self.background_color = RGBColor(250, 250, 250)
            self.title_font_size = Pt(36)
            self.subtitle_font_size = Pt(22)
            self.header_font_size = Pt(28)
            self.content_font_size = Pt(18)

    def _add_title_slide(self, title, subtitle=None):
        slide_layout = self.prs.slide_layouts[0]
        slide = self.prs.slides.add_slide(slide_layout)

        title_shape = slide.shapes.title
        title_shape.text = title

        title_shape.left = Inches(0.5)
        title_shape.top = Inches(2.5)
        title_shape.width = Inches(12.33)
        title_shape.height = Inches(2.0)

        text_frame = title_shape.text_frame
        text_frame.margin_left = Inches(0.2)
        text_frame.margin_right = Inches(0.2)
        text_frame.margin_top = Inches(0.1)
        text_frame.margin_bottom = Inches(0.1)
        text_frame.word_wrap = True

        p = text_frame.paragraphs[0]
        p.font.size = self.title_font_size
        p.font.bold = True
        p.font.color.rgb = self.title_color
        p.alignment = PP_ALIGN.CENTER

        if subtitle:
            if len(slide.placeholders) > 1:
                subtitle_shape = slide.placeholders[1]
                subtitle_shape.text = subtitle

                subtitle_shape.left = Inches(0.5)
                subtitle_shape.top = Inches(4.8)
                subtitle_shape.width = Inches(12.33)
                subtitle_shape.height = Inches(1.0)

                subtitle_frame = subtitle_shape.text_frame
                subtitle_frame.margin_left = Inches(0.2)
                subtitle_frame.margin_right = Inches(0.2)
                subtitle_frame.margin_top = Inches(0.1)
                subtitle_frame.margin_bottom = Inches(0.1)

                p = subtitle_frame.paragraphs[0]
                p.font.size = self.subtitle_font_size
                p.font.color.rgb = self.accent_color
                p.alignment = PP_ALIGN.CENTER

        if self.theme == "minimal":
            left = Inches(3.5)
            top = Inches(4.5)
            width = Inches(6.33)
            height = Inches(0.05)
            line = slide.shapes.add_shape(1, left, top, width, height)
            line.fill.solid()
            line.fill.fore_color.rgb = self.accent_color
            line.line.fill.background()

        return slide

    def _add_section_slide(self, title):
        slide_layout = self.prs.slide_layouts[2] if len(self.prs.slide_layouts) > 2 else self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)

        title_shape = slide.shapes.title
        title_shape.text = title

        title_shape.left = Inches(0.5)
        title_shape.top = Inches(1.0)
        title_shape.width = Inches(12.33)
        title_shape.height = Inches(1.5)

        text_frame = title_shape.text_frame
        text_frame.margin_left = Inches(0.2)
        text_frame.margin_right = Inches(0.2)
        text_frame.margin_top = Inches(0.1)
        text_frame.margin_bottom = Inches(0.1)

        p = text_frame.paragraphs[0]
        p.font.size = self.header_font_size
        p.font.bold = True
        p.font.color.rgb = self.title_color
        p.alignment = PP_ALIGN.CENTER

        if self.theme == "corporate":
            left = Inches(0)
            top = Inches(0)
            width = Inches(1.0)
            height = Inches(7.5)
            sidebar = slide.shapes.add_shape(1, left, top, width, height)
            sidebar.fill.solid()
            sidebar.fill.fore_color.rgb = self.accent_color
            sidebar.line.fill.background()
        elif self.theme == "minimal":
            left = Inches(0.5)
            top = Inches(2.8)
            width = Inches(0.1)
            height = Inches(2.5)
            line = slide.shapes.add_shape(1, left, top, width, height)
            line.fill.solid()
            line.fill.fore_color.rgb = self.accent_color
            line.line.fill.background()

        return slide

    def _add_content_slide(self, title, content_points):
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)

        title_shape = slide.shapes.title
        title_shape.text = title

        title_shape.left = Inches(0.5)
        title_shape.top = Inches(0.3)
        title_shape.width = Inches(12.33)
        title_shape.height = Inches(1.2)

        title_frame = title_shape.text_frame
        title_frame.margin_left = Inches(0.2)
        title_frame.margin_right = Inches(0.2)
        title_frame.margin_top = Inches(0.1)
        title_frame.margin_bottom = Inches(0.1)

        p = title_frame.paragraphs[0]
        p.font.size = self.header_font_size
        p.font.bold = True
        p.font.color.rgb = self.title_color

        if len(slide.placeholders) > 1:
            content = slide.placeholders[1]
        else:
            left = Inches(0.8)
            top = Inches(1.8)
            width = Inches(11.73)
            height = Inches(5.2)
            content = slide.shapes.add_textbox(left, top, width, height)

        content.left = Inches(0.8)
        content.top = Inches(1.8)
        content.width = Inches(11.73)
        content.height = Inches(5.2)

        text_frame = content.text_frame
        text_frame.clear()

        text_frame.margin_left = Inches(0.3)
        text_frame.margin_right = Inches(0.3)
        text_frame.margin_top = Inches(0.2)
        text_frame.margin_bottom = Inches(0.2)
        text_frame.word_wrap = True

        for i, point in enumerate(content_points):
            if point.strip():
                if i == 0:
                    p = text_frame.paragraphs[0]
                else:
                    p = text_frame.add_paragraph()

                p.text = f"• {point.strip()}"
                p.font.size = self.content_font_size
                p.font.color.rgb = self.text_color
                p.level = 0
                p.space_after = Pt(6)

        if self.theme == "corporate":
            left = Inches(0)
            top = Inches(7.0)
            width = Inches(13.33)
            height = Inches(0.5)
            footer = slide.shapes.add_shape(1, left, top, width, height)
            footer.fill.solid()
            footer.fill.fore_color.rgb = self.accent_color
            footer.line.fill.background()
        elif self.theme == "minimal":
            left = Inches(0.8)
            top = Inches(1.6)
            width = Inches(11.73)
            height = Inches(0.03)
            line = slide.shapes.add_shape(1, left, top, width, height)
            line.fill.solid()
            line.fill.fore_color.rgb = self.accent_color
            line.line.fill.background()

        return slide

    def _add_table_slide(self, title, table_data):
        slide_layout = self.prs.slide_layouts[1]
        slide = self.prs.slides.add_slide(slide_layout)

        title_shape = slide.shapes.title
        title_shape.text = title

        title_shape.left = Inches(0.5)
        title_shape.top = Inches(0.3)
        title_shape.width = Inches(12.33)
        title_shape.height = Inches(1.0)

        p = title_shape.text_frame.paragraphs[0]
        p.font.size = self.header_font_size
        p.font.bold = True
        p.font.color.rgb = self.title_color

        if table_data and len(table_data) > 0:
            rows = len(table_data)
            cols = max(len(row) for row in table_data) if table_data else 1

            left = Inches(0.8)
            top = Inches(1.8)
            width = Inches(11.73)
            height = Inches(4.5)

            table = slide.shapes.add_table(rows, cols, left, top, width, height).table

            for row_idx, row_data in enumerate(table_data):
                for col_idx, cell_data in enumerate(row_data):
                    if col_idx < cols:
                        cell = table.cell(row_idx, col_idx)
                        cell.text = str(cell_data)

                        p = cell.text_frame.paragraphs[0]
                        p.font.size = Pt(14)
                        p.font.color.rgb = self.text_color

                        if row_idx == 0:
                            p.font.bold = True
                            p.font.color.rgb = self.title_color

        return slide

    def _detect_tables(self, text_content):
        lines = text_content.strip().split('\n')
        table_candidate_lines = 0

        for line in lines:
            if re.search(r'\s{3,}|\t', line) or line.count('|') >= 2:
                table_candidate_lines += 1

        return table_candidate_lines >= 3

    def _process_table_data(self, content_lines):
        if not content_lines:
            return []

        table_data = []

        for line in content_lines:
            if re.search(r'\s{3,}|\t', line):
                cells = re.split(r'\s{3,}|\t', line)
                cells = [cell.strip() for cell in cells if cell.strip()]

                if cells:
                    table_data.append(cells)
            elif line.count('|') >= 2:
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells:
                    table_data.append(cells)

        return table_data

    def create_presentation(self, document_structure):
        if not isinstance(document_structure, dict):
            document_structure = self._convert_to_structure(document_structure)

        title = document_structure.get('title', 'Document')
        subtitle = document_structure.get('subtitle', '')

        if document_structure.get('version'):
            if subtitle:
                subtitle += f" | Version {document_structure['version']}"
            else:
                subtitle = f"Version {document_structure['version']}"

        if document_structure.get('date'):
            if subtitle:
                subtitle += f" | {document_structure['date']}"
            else:
                subtitle = document_structure['date']

        self._add_title_slide(title, subtitle)

        sections = document_structure.get('sections', [])
        if sections:
            overview_points = [section['title'] for section in sections]
            if overview_points:
                self._add_content_slide("Overview", overview_points[:8])

            for section in sections:
                section_title = section['title']
                section_content = section.get('content', [])

                is_table = isinstance(section_content, list) and len(section_content) > 0 and isinstance(
                    section_content[0], list)

                if is_table:
                    self._add_table_slide(section_title, section_content)
                elif isinstance(section_content, list) and section_content:
                    if len(section_content) <= 6:
                        self._add_content_slide(section_title, section_content)
                    else:
                        chunks = [section_content[i:i + 6] for i in range(0, len(section_content), 6)]
                        for i, chunk in enumerate(chunks):
                            slide_title = section_title if i == 0 else f"{section_title} (cont.)"
                            self._add_content_slide(slide_title, chunk)
                else:
                    continue

        self._add_section_slide("Thank You")

        self.prs.save(self.output_filename)
        print(f"Presentation created and saved as {self.output_filename}")

    def _convert_to_structure(self, text_content):
        import re

        if isinstance(text_content, dict):
            return text_content

        structure = {
            "title": "",
            "subtitle": "",
            "sections": []
        }

        lines = text_content.strip().split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if re.match(r'^#+\s', line) or (line.isupper() and len(line) < 100):
                if not structure["title"]:
                    structure["title"] = line.lstrip('#').strip()
                    continue

                section_title = line.lstrip('#').strip()
                if not section_title:
                    continue

                current_section = {
                    "title": section_title,
                    "content": []
                }
                structure["sections"].append(current_section)
            elif current_section and (line.startswith('*') or line.startswith('-') or re.match(r'^\d+\.', line)):
                item_text = line.lstrip('*-0123456789. \t')
                current_section["content"].append(item_text)

        if not structure["sections"] and text_content:
            structure["sections"] = [{
                "title": "General Information",
                "content": [line.strip() for line in lines if line.strip()]
            }]

        return structure
