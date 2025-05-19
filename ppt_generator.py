import pypdf
from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Pt


import re
import os
import json
import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract_text
from pdfminer.layout import LAParams
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
import ollama  # Importando a biblioteca Ollama

class PdfToPptxConverter:
    def __init__(self, output_filename="presentation.pptx", ollama_processor=None):
        """
        Inicializa o conversor de PDF para PPTX

        Args:
            output_filename (str): Nome do arquivo de saída
            ollama_processor (OllamaProcessor, optional): Processador Ollama
        """
        self.prs = Presentation()
        self.output_filename = output_filename
        self.ollama_processor = ollama_processor

        # Definir o tamanho dos slides como 16:9
        self.prs.slide_width = Inches(13.33)
        self.prs.slide_height = Inches(7.5)

    def _add_title_slide(self, title, subtitle=None):
        """Adiciona um slide de título"""
        slide_layout = self.prs.slide_layouts[0]  # Layout de título
        slide = self.prs.slides.add_slide(slide_layout)

        # Adicionar título
        title_shape = slide.shapes.title
        title_shape.text = title
        title_shape.text_frame.paragraphs[0].font.size = Pt(40)
        title_shape.text_frame.paragraphs[0].font.bold = True

        # Adicionar subtítulo se fornecido
        if subtitle:
            subtitle_shape = slide.placeholders[1]
            subtitle_shape.text = subtitle
            subtitle_shape.text_frame.paragraphs[0].font.size = Pt(24)

    def _add_section_slide(self, title):
        """Adiciona um slide de seção"""
        slide_layout = self.prs.slide_layouts[2]  # Layout de seção
        slide = self.prs.slides.add_slide(slide_layout)

        # Adicionar título
        title_shape = slide.shapes.title
        title_shape.text = title
        title_shape.text_frame.paragraphs[0].font.size = Pt(36)
        title_shape.text_frame.paragraphs[0].font.bold = True

        return slide

    def _add_content_slide(self, title, content_points):
        """Adiciona um slide de conteúdo com pontos"""
        slide_layout = self.prs.slide_layouts[1]  # Layout de conteúdo
        slide = self.prs.slides.add_slide(slide_layout)

        # Adicionar título
        title_shape = slide.shapes.title
        title_shape.text = title
        title_shape.text_frame.paragraphs[0].font.size = Pt(32)
        title_shape.text_frame.paragraphs[0].font.bold = True

        # Adicionar conteúdo
        content = slide.placeholders[1]
        text_frame = content.text_frame
        text_frame.clear()

        for point in content_points:
            if point.strip():  # Verifica se o ponto não está vazio
                p = text_frame.add_paragraph()
                p.text = point
                p.font.size = Pt(20)
                p.level = 0

        return slide

    def _add_table_slide(self, title, table_data):
        """Adiciona um slide com uma tabela"""
        slide_layout = self.prs.slide_layouts[5]  # Layout com título e conteúdo
        slide = self.prs.slides.add_slide(slide_layout)

        # Adicionar título
        title_shape = slide.shapes.title
        title_shape.text = title
        title_shape.text_frame.paragraphs[0].font.size = Pt(32)
        title_shape.text_frame.paragraphs[0].font.bold = True

        # Determinar dimensões da tabela
        rows = len(table_data)
        if rows == 0:
            return slide

        cols = max(len(row) for row in table_data)

        # Adicionar tabela
        left = Inches(0.5)
        top = Inches(2.0)
        width = Inches(12)
        height = Inches(4)

        table = slide.shapes.add_table(rows, cols, left, top, width, height).table

        # Preencher a tabela
        for i, row_data in enumerate(table_data):
            for j, cell_text in enumerate(row_data):
                if j < cols:  # Certificar-se de não exceder o número de colunas
                    cell = table.cell(i, j)
                    cell.text = cell_text

                    # Formatar o texto da célula
                    for paragraph in cell.text_frame.paragraphs:
                        paragraph.font.size = Pt(16)
                        if i == 0:  # Cabeçalho
                            paragraph.font.bold = True

        return slide

    def _detect_tables(self, text_content):
        """Detecta se o texto contém dados tabulares"""
        lines = text_content.strip().split('\n')
        table_candidate_lines = 0

        for line in lines:
            # Verifica padrões de tabela
            if re.search(r'\s{3,}|\t', line) or line.count('|') >= 2:
                table_candidate_lines += 1

        # Se mais de 3 linhas parecem tabelas, considera como uma tabela
        return table_candidate_lines >= 3

    def _process_table_data(self, content_lines):
        """Processa dados de tabela a partir do conteúdo de texto"""
        if not content_lines:
            return []

        table_data = []

        for line in content_lines:
            # Verifica se é uma linha de tabela (tem múltiplos espaços ou tabulações)
            if re.search(r'\s{3,}|\t', line):
                # Divisão baseada em espaços múltiplos ou tabulações
                cells = re.split(r'\s{3,}|\t', line)
                cells = [cell.strip() for cell in cells if cell.strip()]

                if cells:
                    table_data.append(cells)
            elif line.count('|') >= 2:  # Tabela delimitada por pipes
                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells:
                    table_data.append(cells)

        return table_data

    def create_presentation(self, document_structure):
        """
        Cria uma apresentação com base na estrutura do documento

        Args:
            document_structure (dict): Estrutura do documento
        """
        # Slide de título
        title = document_structure.get('title', 'Documento')
        subtitle = document_structure.get('subtitle', '')

        # Adiciona versão e data ao subtítulo se disponíveis
        if document_structure.get('version'):
            if subtitle:
                subtitle += f" | Versão {document_structure['version']}"
            else:
                subtitle = f"Versão {document_structure['version']}"

        if document_structure.get('date'):
            if subtitle:
                subtitle += f" | {document_structure['date']}"
            else:
                subtitle = document_structure['date']

        self._add_title_slide(title, subtitle)

        # Slide de visão geral
        sections = document_structure.get('sections', [])
        if sections:
            overview_points = [section['title'] for section in sections]
            if overview_points:
                self._add_content_slide("Visão Geral", overview_points[:8])

            # Criar slides para cada seção
            for section in sections:
                section_title = section['title']
                section_content = section.get('content', [])

                # Slide de título da seção
                self._add_section_slide(section_title)

                # Verifica se é uma tabela
                is_table = isinstance(section_content, list) and len(section_content) > 0 and isinstance(
                    section_content[0], list)

                if is_table:
                    # É uma tabela, adiciona como slide de tabela
                    self._add_table_slide(section_title, section_content)
                elif isinstance(section_content, list) and section_content:
                    # É uma lista de pontos, adiciona como slide de conteúdo
                    if len(section_content) <= 6:
                        self._add_content_slide(section_title, section_content)
                    else:
                        # Divide em múltiplos slides se tiver muitos pontos
                        chunks = [section_content[i:i + 6] for i in range(0, len(section_content), 6)]
                        for i, chunk in enumerate(chunks):
                            slide_title = section_title if i == 0 else f"{section_title} (cont.)"
                            self._add_content_slide(slide_title, chunk)
                else:
                    # Seção sem conteúdo ou com conteúdo vazio
                    continue

        # Slide final
        self._add_section_slide("Obrigado")

        # Salvar a apresentação
        self.prs.save(self.output_filename)
        print(f"Apresentação criada e salva como {self.output_filename}")

