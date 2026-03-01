import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QComboBox, QLabel, QScrollArea, QGroupBox, 
                             QPushButton, QApplication, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
# Import bind_input để đồng bộ dữ liệu
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(input_tab=None):
    if input_tab is None: return None

    main_win = input_tab.main_window
    motor = main_win.motor
    # Lấy container dữ liệu thô
    mat_params = motor.material_data 
    
    # --- 1. ĐỊNH NGHĨA CÁC HÀM LOGIC TRƯỚC ---
    
    def update_summary_display():
        """Chỉ cập nhật nhãn hiển thị tóm tắt dựa trên Database hiện tại."""
        db = motor.material_database
        if db:
            summary = (
                f"<div style='line-height: 150%;'>"
                f"<p><b>🌍 AIR MEDIUM:</b><br><span style='color:#2980b9;'>{db.air.name}</span> (μr={db.air.relative_permeance})</p>"
                f"<p><b>🧲 HARD MAGNETIC (Magnet):</b><br><span style='color:#c0392b;'>{db.magnet.name}</span><br>"
                f"&nbsp;&nbsp;• Mur: {db.magnet.relative_permeance}<br>"
                f"&nbsp;&nbsp;• Hc: {db.magnet.coercivity} A/m</p>"
                f"<p><b>🏗️ SOFT MAGNETIC (Iron):</b><br><span style='color:#2c3e50;'>{db.iron.name}</span><br>"
                f"&nbsp;&nbsp;• B-H Curve: {len(db.iron.B_H_curve['B_data'])} points</p>"
                f"</div>"
            )
            input_tab.summary_display.setText(summary)

    def handle_refresh():
        """Hàm refresh thông minh: Chỉ nạp lại nếu StateManager báo lỗi thời."""
        if motor is None: return
        # Nếu dữ liệu đã tươi, chỉ cập nhật hiển thị nhãn
        if motor.ready_state.material_database:
            update_summary_display()
            return
            
        motor.require("material_database")
        update_summary_display()
        QApplication.processEvents()

    def on_input_changed():
        """Callback khi sửa dữ liệu trực tiếp tại tab này."""
        if motor is None: return
        motor.just_changed("material_database")
        handle_refresh()

    # Gán vào đối tượng tab để hỗ trợ cơ chế Smart Refresh
    input_tab.refresh = handle_refresh
    input_tab.refresh_content = update_summary_display

    # --- 2. XÂY DỰNG GIAO DIỆN ---
    STYLE_SHEET = """
        QGroupBox { 
            font-weight: bold; border: 1px solid #ccd1d1; 
            border-radius: 6px; margin-top: 15px; background-color: #fcfcfc;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #333; }
        QLabel { font-size: 13px; color: #34495e; }
        QLineEdit, QComboBox { border: 1px solid #bdc3c7; border-radius: 4px; padding: 3px; }
    """
    input_tab.setStyleSheet(STYLE_SHEET)

    main_layout = QHBoxLayout(input_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    splitter = QSplitter(Qt.Horizontal)

    # PANEL TRÁI: Cài đặt (2 phần)
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 5, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setStyleSheet("QScrollArea { background-color: transparent; }")
    
    content_widget = QWidget()
    content_vbox = QVBoxLayout(content_widget)
    content_vbox.setAlignment(Qt.AlignTop)

    # Group 1: Environment
    air_group = QGroupBox("Environment")
    air_form = QFormLayout(air_group)
    air_form.setVerticalSpacing(10)
    
    air_input = bind_input(mat_params, "air", 1, on_input_changed)
    air_input.setFixedWidth(120)
    air_form.addRow("Medium Name:", air_input)
    content_vbox.addWidget(air_group)

    # Group 2: Material Selection
    mat_group = QGroupBox("Core & Magnet Selection")
    mat_form = QFormLayout(mat_group)
    mat_form.setVerticalSpacing(10)

    mag_combo = QComboBox()
    mag_combo.addItems(["NdFe30", "N35", "N42"]) 
    mag_combo.setCurrentText(mat_params.magnet_type)
    mag_combo.setFixedWidth(120)
    mag_combo.currentTextChanged.connect(lambda t: (setattr(mat_params, "magnet_type", t), on_input_changed()))
    mat_form.addRow("Magnet Grade:", mag_combo)

    iron_combo = QComboBox()
    iron_combo.addItems(["steel_1008", "M270_35A", "M400_50A"])
    iron_combo.setCurrentText(mat_params.iron_type)
    iron_combo.setFixedWidth(120)
    iron_combo.currentTextChanged.connect(lambda t: (setattr(mat_params, "iron_type", t), on_input_changed()))
    mat_form.addRow("Iron Core:", iron_combo)
    
    content_vbox.addWidget(mat_group)
    content_vbox.addStretch()

    scroll.setWidget(content_widget)
    left_layout.addWidget(scroll)

    # PANEL PHẢI: Tóm tắt (3 phần)
    right_panel = QFrame()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(5, 0, 0, 0)

    summary_group = QGroupBox("Material Properties Summary")
    summary_layout = QVBoxLayout(summary_group)
    
    input_tab.summary_display = QLabel("Initializing Database...")
    input_tab.summary_display.setAlignment(Qt.AlignTop)
    input_tab.summary_display.setWordWrap(True)
    input_tab.summary_display.setStyleSheet("background-color: #ffffff; padding: 15px; border-radius: 4px; border: 1px solid #dee2e6;")
    
    summary_layout.addWidget(input_tab.summary_display)
    right_layout.addWidget(summary_group)

    btn_recreate = QPushButton("Force Rebuild Material DB")
    btn_recreate.setFixedHeight(40)
    btn_recreate.setStyleSheet("""
        QPushButton { font-weight: bold; background-color: #f0f7fb; border: 1px solid #c5ddec; border-radius: 4px; }
        QPushButton:hover { background-color: #e1f0f7; }
    """)
    btn_recreate.clicked.connect(on_input_changed)
    right_layout.addWidget(btn_recreate)

    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    
    # --- THIẾT LẬP TỈ LỆ 2:3 ---
    splitter.setSizes([400, 600]) 
    splitter.setStretchFactor(0, 2)
    splitter.setStretchFactor(1, 3)
    
    main_layout.addWidget(splitter)

    QTimer.singleShot(100, handle_refresh)
    
    return None