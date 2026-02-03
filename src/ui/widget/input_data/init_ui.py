import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QComboBox, QLabel, QScrollArea, QGroupBox, 
                             QPushButton, QApplication, QLineEdit)
from PyQt5.QtCore import Qt, QTimer
from src.core.material.models.MaterialDataBase import MaterialDataBase

def init_ui(input_tab=None):
    if input_tab is None: return None

    motor = input_tab.main_window.motor
    
    # --- 1. STYLE SHEET "TIÊU CHUẨN VÀNG" (COPY CHUẨN GEOMETRY) ---
    STYLE_SHEET = """
        QGroupBox { 
            font-weight: bold; 
            border: 1px solid #dee2e6; 
            border-radius: 4px;
            margin-top: 15px; 
            background-color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #2c3e50;
        }
        QLabel {
            font-size: 13px;
            color: #34495e;
        }
        QLineEdit, QComboBox {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 3px;
        }
    """
    input_tab.setStyleSheet(STYLE_SHEET)

    # Layout chính
    main_layout = QHBoxLayout(input_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    splitter = QSplitter(Qt.Horizontal)

    # --- 2. HÀM CẬP NHẬT (GLOBAL UPDATE LOGIC) ---
    def update_global_database():
        air_name = input_tab.air_name_edit.text()
        mag_type = input_tab.mag_combo.currentText()
        iron_type = input_tab.iron_combo.currentText()
        
        # Khởi tạo instance mới
        motor.material_database = MaterialDataBase(
            air=air_name, 
            magnet_type=mag_type, 
            iron_type=iron_type
        )
        
        # Cập nhật hiển thị tóm tắt
        db = motor.material_database
        summary = (
            f"<p><b>AIR MEDIUM:</b><br>{db.air.name} (μr={db.air.relative_permeance})</p>"
            f"<p><b>HARD MAGNETIC:</b><br>{db.magnet.name}<br>"
            f" - Mur: {db.magnet.relative_permeance}<br>"
            f" - Hc: {db.magnet.coercivity} A/m</p>"
            f"<p><b>SOFT MAGNETIC:</b><br>{db.iron.name}<br>"
            f" - B-H Data: {len(db.iron.B_H_curve['B_data'])} points</p>"
        )
        input_tab.summary_display.setText(summary)
        QApplication.processEvents()

    # --- 3. PANEL TRÁI: CÀI ĐẶT (SCROLL AREA VỚI GROUP NẰM NGANG) ---
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 10, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    
    content_widget = QWidget()
    content_hbox = QHBoxLayout(content_widget) # Tiêu chuẩn vàng: Group nằm ngang

    # Group 1: General & Air
    air_group = QGroupBox("Environment")
    air_form = QFormLayout(air_group)
    air_form.setVerticalSpacing(10)
    input_tab.air_name_edit = QLineEdit("Default Air")
    input_tab.air_name_edit.editingFinished.connect(update_global_database)
    air_form.addRow("Medium Name:", input_tab.air_name_edit)
    content_hbox.addWidget(air_group)

    # Group 2: Core & Magnet
    mat_group = QGroupBox("Material Selection")
    mat_form = QFormLayout(mat_group)
    mat_form.setVerticalSpacing(10)

    input_tab.mag_combo = QComboBox()
    input_tab.mag_combo.addItems(["N30UH", "N35SH", "N42SH"])
    input_tab.mag_combo.currentTextChanged.connect(update_global_database)
    mat_form.addRow("Magnet Grade:", input_tab.mag_combo)

    input_tab.iron_combo = QComboBox()
    input_tab.iron_combo.addItems(["M350-50A", "M400-50A", "M270-35A"])
    input_tab.iron_combo.currentTextChanged.connect(update_global_database)
    mat_form.addRow("Iron Core:", input_tab.iron_combo)
    
    content_hbox.addWidget(mat_group)

    scroll.setWidget(content_widget)
    left_layout.addWidget(scroll)

    # --- 4. PANEL PHẢI: SUMMARY & FORCE UPDATE ---
    right_panel = QFrame()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)

    # Group hiển thị tóm tắt
    summary_group = QGroupBox("Material Properties Summary")
    summary_layout = QVBoxLayout(summary_group)
    
    input_tab.summary_display = QLabel("Initializing Database...")
    input_tab.summary_display.setAlignment(Qt.AlignTop)
    input_tab.summary_display.setWordWrap(True)
    input_tab.summary_display.setStyleSheet("background-color: #ffffff; padding: 10px; font-family: 'Segoe UI';")
    
    summary_layout.addWidget(input_tab.summary_display)
    right_layout.addWidget(summary_group)

    # Nút bấm Force Recreate chuẩn Geometry
    btn_recreate = QPushButton("Force Rebuild Material DB")
    btn_recreate.setFixedHeight(40)
    btn_recreate.setStyleSheet("""
        QPushButton { 
            font-weight: bold; 
            background-color: #f0f7fb; 
            border: 1px solid #c5ddec;
            border-radius: 4px;
        }
        QPushButton:hover { background-color: #e1f0f7; }
    """)
    btn_recreate.clicked.connect(update_global_database)
    right_layout.addWidget(btn_recreate)

    # Cấu hình Splitter (Tỉ lệ 1:1)
    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 1)
    
    main_layout.addWidget(splitter)

    # Khởi tạo lần đầu sau khi UI sẵn sàng
    QTimer.singleShot(500, update_global_database)
    
    return None