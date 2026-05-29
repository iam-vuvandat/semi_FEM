from reportlab.platypus import Paragraph, Spacer, Table, PageBreak
from ._fig_to_image_flowable import _fig_to_image_flowable

def _build_section_3(story, motor, config):
    """Generates Section 3: Armature Winding Configuration and Layout Image."""
    story.append(Paragraph("3. Armature Winding Configuration", config.h1_style))
    
    wdg = motor.winding_data
    wdg_rows = [
        [Paragraph("<b>Winding Specification</b>", config.table_header), Paragraph("<b>Configuration Setting</b>", config.table_header)],
        [Paragraph("Number of Phases ($m$)", config.table_text), Paragraph(str(wdg.phase), config.table_text)],
        [Paragraph("Total Series Turns Per Coil", config.table_text), Paragraph(str(wdg.turns), config.table_text)],
        [Paragraph("Coil Throw Interval (Slots)", config.table_text), Paragraph(str(wdg.throw), config.table_text)],
        [Paragraph("Winding Layer Assignment Count", config.table_text), Paragraph(str(wdg.winding_layer), config.table_text)],
        [Paragraph("Parallel Circuit Paths Count", config.table_text), Paragraph(str(wdg.parallel_path), config.table_text)]
    ]
    t_wdg = Table(wdg_rows, colWidths=[250, 254])
    t_wdg.setStyle(config.base_table_style)
    story.append(t_wdg)
    story.append(Spacer(1, 10))

    if hasattr(wdg, 'fig_layout') and wdg.fig_layout is not None:
        story.append(Paragraph("3.1 Armature Structural Coil Layout Matrix", config.h2_style))
        img_wdg = _fig_to_image_flowable(wdg.fig_layout, width=480)
        if img_wdg:
            story.append(img_wdg)

    story.append(PageBreak())