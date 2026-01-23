import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QComboBox, QLabel, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(winding_tab=None):
    if winding_tab is None: return None

    motor = winding_tab.main_window.motor
    main_layout = QHBoxLayout(winding_tab)
    splitter = QSplitter(Qt.Horizontal)

    # --- 1. HÀM CẬP NHẬT BẢNG MA TRẬN (REFRESH LOGIC) ---
    def refresh_winding_ui():
        """Cập nhật lại bảng hiển thị ma trận dây quấn"""
        matrix = motor.winding_matrix
        if matrix is None:
            winding_tab.matrix_table.setRowCount(0)
            return

        rows, cols = matrix.shape
        table = winding_tab.matrix_table
        table.setRowCount(rows)
        table.setColumnCount(cols)
        
        # Tiêu đề cột (Pha A, B, C...)
        headers = [f"Phase {chr(65+i)}" for i in range(cols)]
        table.setHorizontalHeaderLabels(headers)
        
        # Tiêu đề hàng (Rãnh 1, 2, 3...)
        row_headers = [f"Slot {i+1}" for i in range(rows)]
        table.setVerticalHeaderLabels(row_headers)

        # Điền dữ liệu và tô màu trực quan
        for i in range(rows):
            for j in range(cols):
                val = matrix[i, j]
                item = QTableWidgetItem(f"{val:g}")
                item.setTextAlignment(Qt.AlignCenter)
                
                # Tô màu để dễ quan sát chiều dòng điện
                if val > 0:
                    item.setBackground(QColor("#FFF59D")) # Vàng nhạt (Chiều dương)
                elif val < 0:
                    item.setBackground(QColor("#81D4FA")) # Xanh nhạt (Chiều âm)
                
                table.setItem(i, j, item)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # --- 2. PHẦN BÊN TRÁI: NHẬP LIỆU THÔNG SỐ ---
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    
    input_frame = QFrame()
    input_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;")
    form = QFormLayout(input_frame)

    # Sử dụng bind_input với callback là refresh_winding_ui
    # unit_factor=1 vì đây là các biến đếm (int)
    form.addRow("Number of Phases:", bind_input(motor, "phase", 1, refresh_winding_ui))
    form.addRow("Turns per Coil:", bind_input(motor, "turns", 1, refresh_winding_ui))
    form.addRow("Coil Throw (y):", bind_input(motor, "throw", 1, refresh_winding_ui))
    form.addRow("Parallel Paths (a):", bind_input(motor, "parallel_path", 1, refresh_winding_ui))
    form.addRow("Winding Layers:", bind_input(motor, "winding_layer", 1, refresh_winding_ui))

    # Winding Type Combo
    type_combo = QComboBox()
    type_combo.addItems(["concentrated", "distributed"])
    type_combo.setCurrentText(motor.winding_type)
    
    def on_type_changed(text):
        motor.winding_type = text
        motor.reload() # Tính lại ma trận
        refresh_winding_ui()
        
    type_combo.currentTextChanged.connect(on_type_changed)
    form.addRow("Winding Type:", type_combo)

    left_layout.addWidget(QLabel("<b>Winding Parameters</b>"))
    left_layout.addWidget(input_frame)
    left_layout.addStretch()

    # --- 3. PHẦN BÊN PHẢI: HIỂN THỊ MA TRẬN ---
    right_container = QWidget()
    right_layout = QVBoxLayout(right_container)
    
    winding_tab.matrix_table = QTableWidget()
    winding_tab.matrix_table.setEditTriggers(QTableWidget.NoEditTriggers) # Chỉ xem, không sửa trực tiếp trên bảng
    
    right_layout.addWidget(QLabel("<b>Winding Matrix Preview (Slot vs Phase)</b>"))
    right_layout.addWidget(winding_tab.matrix_table)

    # Thiết lập Splitter
    splitter.addWidget(left_container)
    splitter.addWidget(right_container)
    splitter.setStretchFactor(1, 2)
    
    main_layout.addWidget(splitter)

    # Hiển thị dữ liệu lần đầu khi mở tab
    refresh_winding_ui()
    
    return None