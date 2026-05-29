from reportlab.platypus import Paragraph, Spacer, Table

def _build_computational_performance(story, record, config):
    """
    Generates Section 5: Computational Performance & Resource Utilization.
    Directly extracts and displays solver execution times, hardware resource usage,
    and discretization scales from the core record variables without modification.
    """
    story.append(Paragraph("5. Computational Performance & Resource Utilization", config.h1_style))
    story.append(Paragraph("Quantitative comparison of solver execution speed, numerical scale, and computational resource efficiency:", config.body_style))
    
    # 1. Trích xuất trực tiếp các thông số hiệu năng thời gian và bộ nhớ phần cứng
    mbgrn_time = f"{record.time_solved:.3f} s" if hasattr(record, "time_solved") and record.time_solved is not None else "N/A"
    fem_time = f"{record.total_time_fem:.1f} s" if hasattr(record, "total_time_fem") and record.total_time_fem is not None else "N/A"
    
    mbgrn_mem = f"{record.memory_used:.1f} MB" if hasattr(record, "memory_used") and record.memory_used is not None else "N/A"
    fem_mem = f"{record.memory_used_fem:.1f} MB" if hasattr(record, "memory_used_fem") and record.memory_used_fem is not None else "N/A"

    # 2. Trích xuất trực tiếp các thông số quy mô toán học (Lưới và Ma trận hệ phương trình)
    mbgrn_elements = f"{record.elements:,}" if hasattr(record, "elements") and record.elements is not None else "N/A"
    fem_elements = f"{record.total_elements_fem:,}" if hasattr(record, "total_elements_fem") and record.total_elements_fem is not None else "N/A"

    mbgrn_matrix = f"{record.matrix_size:,}" if hasattr(record, "matrix_size") and record.matrix_size is not None else "N/A"
    fem_matrix = f"{record.matrix_size_fem:,}" if hasattr(record, "matrix_size_fem") and record.matrix_size_fem is not None else "N/A"

    # 3. Tổ chức cấu trúc ma trận bảng dữ liệu đối chiếu hiệu năng máy tính thuần túy
    performance_rows = [
        [Paragraph("<b>Performance Metric Summary</b>", config.table_header), 
         Paragraph("<b>MBGRN Solver</b>", config.table_header), 
         Paragraph("<b>FEM Reference</b>", config.table_header),
         Paragraph("<b>Computational Note</b>", config.table_header)],
        
        [Paragraph("Total Computation Execution Time", config.table_text), 
         Paragraph(mbgrn_time, config.table_text), 
         Paragraph(fem_time, config.table_text), 
         Paragraph("Transient Solver Steps", config.table_text)],
        
        [Paragraph("Peak Memory Footprint (RAM)", config.table_text), 
         Paragraph(mbgrn_mem, config.table_text), 
         Paragraph(fem_mem, config.table_text), 
         Paragraph("Optimized Dynamic Memory", config.table_text)],
        
        [Paragraph("Total Mesh / Discretized Elements", config.table_text), 
         Paragraph(mbgrn_elements, config.table_text), 
         Paragraph(fem_elements, config.table_text), 
         Paragraph("Domain Discretization", config.table_text)],
        
        [Paragraph("Max Linear System Matrix Size", config.table_text), 
         Paragraph(mbgrn_matrix, config.table_text), 
         Paragraph(fem_matrix, config.table_text), 
         Paragraph("Degrees of Freedom", config.table_text)]
    ]
    
    # 4. Khởi tạo đối tượng Table tuân thủ colWidths tiêu chuẩn vừa khít biên lề
    t_perf = Table(performance_rows, colWidths=[184, 110, 110, 100])
    t_perf.setStyle(config.base_table_style)
    
    story.append(t_perf)
    story.append(Spacer(1, 14))