from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import TableStyle

class ReportConfig:
    """
    Centralized configuration class for electrical machine simulation reports.
    Manages typography styles, monochrome color palettes, and global table configurations.
    """
    def __init__(self):
        styles = getSampleStyleSheet()
        
        # 1. Monochrome Palette Definitions (No Color / Black & White)
        self.primary_color = colors.black
        self.secondary_color = colors.black
        self.text_dark = colors.black
        self.text_muted = colors.black
        self.bg_header = colors.white
        self.bg_alt_row = colors.white
        self.grid_color = colors.black

        # 2. Typography & Styles Configuration (Times New Roman Equivalent)
        self.title_style = ParagraphStyle(
            'DocTitle', parent=styles['Title'], fontName='Times-Bold', fontSize=22, leading=26,
            textColor=self.primary_color, alignment=0, spaceAfter=6
        )
        self.subtitle_style = ParagraphStyle(
            'DocSub', parent=styles['Normal'], fontName='Times-Italic', fontSize=10, leading=14,
            textColor=self.text_muted, spaceAfter=15
        )
        
        # === KHỐI CẤU HÌNH THIẾU CẦN BỔ SUNG ===
        self.meta_label_style = ParagraphStyle(
            'MetaLabel', parent=styles['Normal'], fontName='Times-Bold', fontSize=11, leading=15,
            textColor=self.text_dark
        )
        self.meta_val_style = ParagraphStyle(
            'MetaValue', parent=styles['Normal'], fontName='Times-Roman', fontSize=11, leading=15,
            textColor=self.text_dark
        )
        self.desc_style = ParagraphStyle(
            'ProjectDesc', parent=styles['Normal'], fontName='Times-Roman', fontSize=10.5, leading=16,
            textColor=self.text_dark, spaceBefore=10
        )
        # =======================================

        self.h1_style = ParagraphStyle(
            'SectionH1', parent=styles['Heading1'], fontName='Times-Bold', fontSize=13, leading=17,
            textColor=self.primary_color, spaceBefore=14, spaceAfter=8, keepWithNext=True
        )
        self.h2_style = ParagraphStyle(
            'SubSectionH2', parent=styles['Heading2'], fontName='Times-Bold', fontSize=11, leading=15,
            textColor=self.secondary_color, spaceBefore=10, spaceAfter=6, keepWithNext=True
        )
        self.body_style = ParagraphStyle(
            'ReportBody', parent=styles['Normal'], fontName='Times-Roman', fontSize=10, leading=14,
            textColor=self.text_dark, spaceAfter=6
        )
        self.table_text = ParagraphStyle(
            'TableText', parent=styles['Normal'], fontName='Times-Roman', fontSize=9.5, leading=13
        )
        self.table_header = ParagraphStyle(
            'TableHeader', parent=styles['Normal'], fontName='Times-Bold', fontSize=9.5, leading=13,
            textColor=self.primary_color
        )

        # 3. Universal Table Grid Layout Style (Clean Black & White Grid)
        self.base_table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.bg_header),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.bg_alt_row]),
            ('GRID', (0, 0), (-1, -1), 0.5, self.grid_color),
            ('LINEBELOW', (0, 0), (-1, 0), 1.0, self.primary_color),
        ])