import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QComboBox, QLabel, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(winding_tab=None):
    if winding_tab is None: return None

    motor = winding_tab.main_window.motor
    winding_data = motor.winding_data 
    
    # Cờ kiểm soát để không reload khi vừa mở giao diện
    winding_tab._is_init = True 
    
    main_layout = QHBoxLayout(winding_tab)
    main_layout.setContentsMargins(15, 15, 15, 15)
    splitter = QSplitter(Qt.Horizontal)

    # --- 1. REFRESH LOGIC ---
    def refresh_winding_ui():
        # Chỉ reload khi không phải đang khởi tạo lần đầu
        if not winding_tab._is_init:
            motor.reload()
        
        winding_tab._is_init = False
        matrix = winding_data.winding_matrix 
        
        if matrix is None:
            winding_tab.matrix_table.setRowCount(0)
            return

        rows, cols = matrix.shape
        table = winding_tab.matrix_table
        table.setRowCount(rows)
        table.setColumnCount(cols)
        
        table.setHorizontalHeaderLabels([f"Phase {chr(65+i)}" for i in range(cols)])
        table.setVerticalHeaderLabels([f"Slot {i+1}" for i in range(rows)])

        for i in range(rows):
            for j in range(cols):
                val = matrix[i, j]
                item = QTableWidgetItem(f"{val:g}")
                item.setTextAlignment(Qt.AlignCenter)
                if val > 0: item.setBackground(QColor("#FFF59D"))
                elif val < 0: item.setBackground(QColor("#81D4FA"))
                table.setItem(i, j, item)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # --- 2. LEFT PANEL: CONFIGURATION ---
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    left_layout.setContentsMargins(0, 0, 10, 0)
    
    input_frame = QFrame()
    input_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 6px;")
    
    form = QFormLayout(input_frame)
    # Tăng khoảng cách để bố cục không bị dày
    form.setVerticalSpacing(18) 
    form.setHorizontalSpacing(20)
    form.setContentsMargins(15, 20, 15, 20)

    form.addRow("Number of Phases:",    bind_input(winding_data, "phase", 1, refresh_winding_ui))
    form.addRow("Turns per Coil:",      bind_input(winding_data, "turns", 1, refresh_winding_ui))
    form.addRow("Coil Throw (y):",      bind_input(winding_data, "throw", 1, refresh_winding_ui))
    form.addRow("Parallel Paths (a):",  bind_input(winding_data, "parallel_path", 1, refresh_winding_ui))
    form.addRow("Winding Layers:",      bind_input(winding_data, "winding_layer", 1, refresh_winding_ui))

    type_combo = QComboBox()
    type_combo.addItems(["concentrated", "distributed"])
    type_combo.setCurrentText(winding_data.winding_type)
    type_combo.currentTextChanged.connect(lambda t: [setattr(winding_data, "winding_type", t), refresh_winding_ui()])
    form.addRow("Winding Type:", type_combo)

    left_layout.addWidget(QLabel("<b>Winding Configuration</b>"))
    left_layout.addWidget(input_frame)
    left_layout.addStretch()

    # --- 3. RIGHT PANEL: MATRIX PREVIEW ---
    right_container = QWidget()
    right_layout = QVBoxLayout(right_container)
    right_layout.setContentsMargins(10, 0, 0, 0)
    
    winding_tab.matrix_table = QTableWidget()
    winding_tab.matrix_table.setAlternatingRowColors(True)
    
    right_layout.addWidget(QLabel("<b>Winding Matrix Preview (Auto-calculated)</b>"))
    right_layout.addWidget(winding_tab.matrix_table)

    splitter.addWidget(left_container)
    splitter.addWidget(right_container)
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 2) 
    main_layout.addWidget(splitter)

    refresh_winding_ui()
    return None