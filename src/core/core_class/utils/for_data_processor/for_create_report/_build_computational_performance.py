from reportlab.platypus import Paragraph, Spacer, Table

def _build_computational_performance(story, motor, config):
    """
    Generates Section 5: Computational Performance & Resource Utilization.
    Accepts the motor entity as a parameter and extracts metrics from motor.record.
    Computes and displays the ratio comparison directly within the table matrix.
    """
    story.append(Paragraph("5. Computational Performance & Resource Utilization", config.h1_style))
    story.append(Paragraph("Quantitative comparison of solver execution speed, numerical scale, and computational resource efficiency:", config.body_style))
    
    # Trích xuất thực thể record từ đối tượng motor truyền vào
    record = motor.record

    # 1. Khởi tạo giá trị thô từ record
    t_mbgrn = record.time_solved if hasattr(record, "time_solved") else None
    t_fem = record.total_time_fem if hasattr(record, "total_time_fem") else None
    
    m_mbgrn = record.memory_used if hasattr(record, "memory_used") else None
    m_fem = record.memory_used_fem if hasattr(record, "memory_used_fem") else None

    e_mbgrn = record.elements if hasattr(record, "elements") else None
    e_fem = record.total_elements_fem if hasattr(record, "total_elements_fem") else None

    mat_mbgrn = record.matrix_size if hasattr(record, "matrix_size") else None
    mat_fem = record.matrix_size_fem if hasattr(record, "matrix_size_fem") else None

    # 2. Định dạng chuỗi hiển thị giá trị thô cho các ô trong bảng
    mbgrn_time_str = f"{t_mbgrn:.3f} s" if t_mbgrn is not None else "N/A"
    fem_time_str = f"{t_fem:.1f} s" if t_fem is not None else "N/A"
    
    mbgrn_mem_str = f"{m_mbgrn:.1f} MB" if m_mbgrn is not None else "N/A"
    fem_mem_str = f"{m_fem:.1f} MB" if m_fem is not None else "N/A"

    mbgrn_elem_str = f"{e_mbgrn:,}" if e_mbgrn is not None else "N/A"
    fem_elem_str = f"{e_fem:,}" if e_fem is not None else "N/A"

    mbgrn_mat_str = f"{mat_mbgrn:,}" if mat_mbgrn is not None else "N/A"
    fem_mat_str = f"{mat_fem:,}" if mat_fem is not None else "N/A"

    # 3. Tính toán tỉ lệ so sánh số lần trực tiếp (Bảo vệ lỗi chia cho 0 hoặc None)
    ratio_time = f"{t_fem / t_mbgrn:.1f}x faster" if t_fem and t_mbgrn else "N/A"
    ratio_mem  = f"{m_fem / m_mbgrn:.1f}x lower" if m_fem and m_mbgrn else "N/A"
    ratio_elem = f"{e_fem / e_mbgrn:.1f}x fewer" if e_fem and e_mbgrn else "N/A"
    ratio_mat  = f"{mat_fem / mat_mbgrn:.1f}x smaller" if mat_fem and mat_mbgrn else "N/A"

    # 4. Tổ chức cấu trúc ma trận bảng dữ liệu đối chiếu hiệu năng với cột tỉ lệ mới
    performance_rows = [
        [Paragraph("<b>Performance Metric Summary</b>", config.table_header), 
         Paragraph("<b>MBGRN Solver</b>", config.table_header), 
         Paragraph("<b>FEM Reference</b>", config.table_header),
         Paragraph("<b>Comparison Ratio</b>", config.table_header)],
        
        [Paragraph("Total Computation Execution Time", config.table_text), 
         Paragraph(mbgrn_time_str, config.table_text), 
         Paragraph(fem_time_str, config.table_text), 
         Paragraph(ratio_time, config.table_text)],
        
        [Paragraph("Memory used", config.table_text), 
         Paragraph(mbgrn_mem_str, config.table_text), 
         Paragraph(fem_mem_str, config.table_text), 
         Paragraph(ratio_mem, config.table_text)],
        
        [Paragraph("Total Elements", config.table_text), 
         Paragraph(mbgrn_elem_str, config.table_text), 
         Paragraph(fem_elem_str, config.table_text), 
         Paragraph(ratio_elem, config.table_text)],
        
        [Paragraph("System matrix size", config.table_text), 
         Paragraph(mbgrn_mat_str, config.table_text), 
         Paragraph(fem_mat_str, config.table_text), 
         Paragraph(ratio_mat, config.table_text)]
    ]
    
    # 5. Khởi tạo đối tượng Table tuân thủ colWidths tiêu chuẩn vừa khít biên lề 504 pt
    t_perf = Table(performance_rows, colWidths=[184, 110, 110, 100])
    t_perf.setStyle(config.base_table_style)
    
    story.append(t_perf)
    story.append(Spacer(1, 14))