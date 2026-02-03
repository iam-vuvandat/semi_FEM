import paths
import numpy as np
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QComboBox, QLabel, QScrollArea, QGroupBox, 
                             QPushButton, QApplication, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(winding_tab=None):
    if winding_tab is None: return None

    main_win = winding_tab.main_window
    motor = main_win.motor
    winding_data = motor.winding_data 
    
    # Thiết lập Layout chính (Giống hệt Geometry)
    main_layout = QHBoxLayout(winding_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    splitter = QSplitter(Qt.Horizontal)

    # --- HÀM CẬP NHẬT TOÀN HỆ THỐNG ---
    def global_update():
        if motor is None: return
        
        # 1. Reload logic lõi
        motor.reload() 
        
        # 2. Cập nhật bảng Ma trận dây quấn
        matrix = winding_data.winding_matrix 
        table = winding_tab.matrix_table
        if matrix is not None:
            rows, cols = matrix.shape
            table.setRowCount(rows)
            table.setColumnCount(cols)
            table.setHorizontalHeaderLabels([f"Ph {chr(65+i)}" for i in range(cols)])
            for i in range(rows):
                for j in range(cols):
                    val = matrix[i, j]
                    item = QTableWidgetItem(f"{val:g}")
                    item.setTextAlignment(Qt.AlignCenter)
                    if val > 0: item.setBackground(QColor("#FFF59D"))
                    elif val < 0: item.setBackground(QColor("#81D4FA"))
                    table.setItem(i, j, item)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 3. Ép giao diện cập nhật
        QApplication.processEvents()

    # --- PANEL TRÁI: CONFIGURATION (SCROLL AREA) ---
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 10, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    
    content_widget = QWidget()
    content_hbox = QHBoxLayout(content_widget) # Các group nằm ngang giống Geometry

    def create_winding_group(title, attributes):
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                border: 1px solid #dee2e6; 
                border-radius: 4px;
                margin-top: 15px; 
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QFormLayout(group)
        layout.setVerticalSpacing(10)
        
        for attr, label in attributes:
            if hasattr(winding_data, attr):
                # Gắn global_update vào để thay đổi là cập nhật ngay
                input_widget = bind_input(winding_data, attr, 1, global_update)
                layout.addRow(f"{label}:", input_widget)
        return group

    # Nhóm 1: Thông số cơ bản
    topo_attrs = [
        ("phase", "Phases"),
        ("winding_layer", "Layers"),
        ("parallel_path", "Parallel Paths (a)")
    ]
    # Nhóm 2: Thông số bối dây
    coil_attrs = [
        ("turns", "Turns per Coil"),
        ("throw", "Coil Throw (y)")
    ]

    content_hbox.addWidget(create_winding_group("Winding Topology", topo_attrs))
    content_hbox.addWidget(create_winding_group("Coil Parameters", coil_attrs))
    
    scroll.setWidget(content_widget)
    left_layout.addWidget(scroll)

    # --- PANEL PHẢI: PREVIEW (MATRIX TABLE) ---
    right_panel = QFrame()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)

    # Tiêu đề bảng giống phong cách Label bên phải của Đạt
    right_layout.addWidget(QLabel("<b>Winding Matrix Preview</b>"))
    
    winding_tab.matrix_table = QTableWidget()
    winding_tab.matrix_table.setAlternatingRowColors(True)
    winding_tab.matrix_table.setStyleSheet("border: 1px solid #dee2e6; border-radius: 4px;")
    right_layout.addWidget(winding_tab.matrix_table)

    # Nút Force Recreate chuẩn "Tiêu chuẩn vàng"
    btn_reload = QPushButton("Force Recalculate Winding")
    btn_reload.setFixedHeight(40)
    btn_reload.setStyleSheet("""
        QPushButton { 
            font-weight: bold; 
            background-color: #f0f7fb; 
            border: 1px solid #c5ddec;
            border-radius: 4px;
        }
        QPushButton:hover { background-color: #e1f0f7; }
    """)
    btn_reload.clicked.connect(global_update)
    right_layout.addWidget(btn_reload)

    # Cấu hình Splitter
    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setStretchFactor(0, 1) 
    splitter.setStretchFactor(1, 1) 
    
    main_layout.addWidget(splitter)
    
    # Khởi tạo lần đầu sau 500ms
    QTimer.singleShot(500, global_update)
    
    return None