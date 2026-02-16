import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QLabel, QScrollArea, QGroupBox, QComboBox, 
                             QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

# Import bind_input từ project của bạn
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(winding_tab=None):
    if winding_tab is None: return None

    main_win = winding_tab.main_window
    motor = main_win.motor
    winding_data = motor.winding_data 
    
    # --- Layout chính ---
    main_layout = QHBoxLayout(winding_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    splitter = QSplitter(Qt.Horizontal)

    # --- HÀM CẬP NHẬT GIAO DIỆN ---
    def global_update():
        if motor is None: return
        
        # 1. Tính toán lại logic lõi
        motor.reload() 
        
        # 2. Cập nhật Panel Phải (Nội dung động)
        update_right_panel_content()
        
        QApplication.processEvents()

    # --- LOGIC XỬ LÝ PANEL PHẢI ---
    def update_right_panel_content():
        # Lấy chế độ hiển thị từ ComboBox
        mode = winding_tab.view_selector.currentText()
        
        # Xóa widget cũ trong layout nội dung
        clear_layout(winding_tab.right_content_layout)
        
        # Mapping các chế độ với dữ liệu
        # Dạng tuple: (Loại, Tên thuộc tính trong winding_data)
        mapping = {
            "Winding Matrix (Ampe-turns)": ("matrix", "slot_matrix"),    # Ma trận dây quấn
            "Tooth Matrix (MMF Potential)":("matrix", "winding_matrix"), # Ma trận răng
            "Layout Plot (Linear)":        ("plot", "fig_layout"),
            "Polar Plot (Circular)":       ("plot", "fig_polar"),
            "Star of Slots (Phasors)":     ("plot", "fig_star"),
            "MMF Distribution":            ("plot", "fig_mmk"),
            "Winding Factors":             ("plot", "fig_wf")
        }
        
        data_type, attr_name = mapping.get(mode, (None, None))
        
        if data_type == "matrix":
            matrix = getattr(winding_data, attr_name, None)
            widget = create_matrix_widget(matrix)
            winding_tab.right_content_layout.addWidget(widget)
            
        elif data_type == "plot":
            # Lấy đối tượng Figure từ motor.winding_data
            fig = getattr(winding_data, attr_name, None)
            widget = create_plot_widget(fig)
            winding_tab.right_content_layout.addWidget(widget)

    # Hàm tạo Widget Bảng Ma trận
    def create_matrix_widget(matrix):
        table = QTableWidget()
        if matrix is not None:
            rows, cols = matrix.shape
            table.setRowCount(rows)
            table.setColumnCount(cols)
            table.setHorizontalHeaderLabels([f"Ph {chr(65+i)}" for i in range(cols)])
            table.setVerticalHeaderLabels([f"Slot {i+1}" for i in range(rows)])
            
            for i in range(rows):
                for j in range(cols):
                    val = matrix[i, j]
                    item = QTableWidgetItem(f"{val:g}")
                    item.setTextAlignment(Qt.AlignCenter)
                    
                    # Tô màu trực quan
                    if val > 0: item.setBackground(QColor("#FFF59D")) # Vàng
                    elif val < 0: item.setBackground(QColor("#81D4FA")) # Xanh
                    else: item.setBackground(QColor("#FFFFFF"))
                    
                    table.setItem(i, j, item)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    # Hàm tạo Widget Đồ thị (Nhúng Matplotlib)
    def create_plot_widget(fig):
        if fig is None:
            lbl = QLabel("No Data Available. Please modify parameters to calculate.")
            lbl.setAlignment(Qt.AlignCenter)
            return lbl
        
        # Tạo Canvas từ Figure có sẵn của SWAT-EM
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas.updateGeometry()
        return canvas

    # Hàm tiện ích xóa layout cũ
    def clear_layout(layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # ==========================
    # XÂY DỰNG GIAO DIỆN
    # ==========================

    # --- PANEL TRÁI (Configuration) ---
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 10, 0)
    
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    content_widget = QWidget()
    content_vbox = QVBoxLayout(content_widget) 

    def create_group(title, attrs):
        grp = QGroupBox(title)
        grp.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #dee2e6; margin-top: 10px; } QGroupBox::title { left: 10px; }")
        layout = QFormLayout(grp)
        for attr, lbl in attrs:
            if hasattr(winding_data, attr):
                # Khi thay đổi input -> Gọi global_update -> Tính lại -> Cập nhật Plot/Matrix
                layout.addRow(f"{lbl}:", bind_input(winding_data, attr, 1, global_update))
        return grp

    content_vbox.addWidget(create_group("Topology", [("phase", "Phases"), ("winding_layer", "Layers"), ("parallel_path", "Parallel Paths")]))
    content_vbox.addWidget(create_group("Coil Params", [("turns", "Turns/Coil"), ("throw", "Coil Throw")]))
    content_vbox.addStretch()
    scroll.setWidget(content_widget)
    left_layout.addWidget(scroll)

    # --- PANEL PHẢI (Dynamic View) ---
    right_panel = QFrame()
    right_panel.setFrameShape(QFrame.StyledPanel)
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)

    # 1. Header: Selector
    header_layout = QHBoxLayout()
    header_lbl = QLabel("<b>Display Mode:</b>")
    
    winding_tab.view_selector = QComboBox()
    winding_tab.view_selector.addItems([
        "Winding Matrix (Ampe-turns)",
        "Tooth Matrix (MMF Potential)",
        "Layout Plot (Linear)",
        "Polar Plot (Circular)",
        "Star of Slots (Phasors)",
        "MMF Distribution",
        "Winding Factors"
    ])
    # Khi chọn item khác -> Chỉ cần cập nhật nội dung panel phải (không cần tính lại motor)
    winding_tab.view_selector.currentIndexChanged.connect(update_right_panel_content)
    
    header_layout.addWidget(header_lbl)
    header_layout.addWidget(winding_tab.view_selector)
    header_layout.addStretch()
    
    # 2. Body: Content Area
    winding_tab.right_content_widget = QWidget()
    winding_tab.right_content_layout = QVBoxLayout(winding_tab.right_content_widget)
    winding_tab.right_content_layout.setContentsMargins(0, 10, 0, 0)

    right_layout.addLayout(header_layout)
    right_layout.addWidget(winding_tab.right_content_widget)

    # --- Kết nối Splitter ---
    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 2)
    main_layout.addWidget(splitter)
    
    # Khởi chạy lần đầu
    QTimer.singleShot(500, global_update)
    
    return None