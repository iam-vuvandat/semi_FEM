from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak

def _create_header_section(story, config):
    """
    Generates the main title, subtitle, fixed author metadata, project description, 
    and forces a page break to move technical content to the next page.
    """
    # 1. Tiêu đề chính báo cáo
    story.append(Paragraph("Axial Flux Electrical Machine Design Report", config.title_style))
    story.append(Paragraph("Automated Design Summary Generated via Python Simulation Suite", config.subtitle_style))
    story.append(Spacer(1, 15))
    
    # 2. Khối thông tin Dự án cố định (Sử dụng bảng ẩn để căn lề thẳng hàng)
    meta_data = [
        [Paragraph("Simulation Solver:", config.meta_label_style), 
         Paragraph("Three dimension mesh based generated reluctance network (MBGRN)", config.meta_val_style)],
        [Paragraph("Author / Lead Engineer:", config.meta_label_style), 
         Paragraph("Dat Van Vu", config.meta_val_style)]
    ]
    
    meta_table = Table(meta_data, colWidths=[130, 350])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))
    
    # 3. Khối mô tả dự án cố định
    project_description = (
        "This simulation report details the electromagnetic performance, validation parameters, "
        "and core geometric data of an axial flux electrical machine design. All transient waveforms "
        "and performance metrics are processed and validated through the automated simulation pipeline."
    )
    story.append(Paragraph("Project Description:", config.meta_label_style))
    story.append(Paragraph(project_description, config.desc_style))
    
    # 4. Ép buộc ngắt trang sang trang mới
    story.append(PageBreak())