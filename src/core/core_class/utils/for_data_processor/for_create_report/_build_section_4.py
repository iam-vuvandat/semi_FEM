from reportlab.platypus import Paragraph, Spacer, Table

def _build_section_4(story, motor, config):
    """
    Generates Section 4: Performance Metrics Validation Summary.
    Accepts the motor entity as a parameter and extracts pre-computed average 
    mechanical power data and its relative error directly from motor.record.
    """
    story.append(Paragraph("4. Performance Metrics Validation Summary", config.h1_style))
    story.append(Paragraph("Integral average values computed across a complete steady-state verification cycle:", config.body_style))
    
    # Trích xuất thực thể record từ đối tượng motor truyền vào
    record = motor.record
    
    # 2. Trích xuất dữ liệu Công suất và Sai số tương đối trung bình từ thực thể record nội bộ
    mbgrn_pow = f"{record.average_mechanical_power:.2f} W" if hasattr(record, "average_mechanical_power") and record.average_mechanical_power is not None else "N/A"
    fem_pow = f"{record.average_mechanical_power_fem:.2f} W" if hasattr(record, "average_mechanical_power_fem") and record.average_mechanical_power_fem is not None else "N/A"
    pow_err = f"{record.mechanical_power_average_error:.2f}%" if hasattr(record, "mechanical_power_average_error") and record.mechanical_power_average_error is not None else "N/A"

    # 3. Định hình cấu trúc ma trận dòng/cột hiển thị dữ liệu thuần túy lên bảng
    kpi_rows = [
        [Paragraph("<b>Performance Metric Summary</b>", config.table_header), 
         Paragraph("<b>MBGRN Solver</b>", config.table_header), 
         Paragraph("<b>FEM Reference</b>", config.table_header),
         Paragraph("<b>Relative Error (%)</b>", config.table_header)],
        [Paragraph("Average Mechanical Output Power", config.table_text), 
         Paragraph(mbgrn_pow, config.table_text), 
         Paragraph(fem_pow, config.table_text), 
         Paragraph(pow_err, config.table_text)]
    ]
    
    # 4. Khởi tạo đối tượng Table với độ rộng các cột tối ưu hóa [184, 110, 110, 100]
    t_kpi = Table(kpi_rows, colWidths=[184, 110, 110, 100])
    t_kpi.setStyle(config.base_table_style)  # Áp dụng lưới đường viền đen trắng tối giản từ cấu hình chung
    
    # 5. Đẩy thành phần bảng vào luồng biên dịch của tài liệu PDF
    story.append(t_kpi)
    story.append(Spacer(1, 14))