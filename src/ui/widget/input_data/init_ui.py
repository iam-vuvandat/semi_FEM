import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QComboBox, QLabel, QLineEdit)
from PyQt5.QtCore import Qt
from src.core.material.models.MaterialDataBase import MaterialDataBase
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(input_tab=None):
    if input_tab is None: return None

    motor = input_tab.main_window.motor
    main_layout = QHBoxLayout(input_tab)
    splitter = QSplitter(Qt.Horizontal)

    # --- 1. HÀM CẬP NHẬT DATABASE (RECREATE LOGIC) ---
    def update_global_database():
        """Khởi tạo lại toàn bộ MaterialDataBase cho motor"""
        air_name = input_tab.air_name_edit.text()
        mag_type = input_tab.mag_combo.currentText()
        iron_type = input_tab.iron_combo.currentText()
        
        # Khởi tạo instance mới của MaterialDataBase
        # Điều này sẽ tự động tạo các object Air, Magnet, Iron bên trong
        motor.material_database = MaterialDataBase(
            air=air_name, 
            magnet_type=mag_type, 
            iron_type=iron_type
        )
        
        # Cập nhật thông tin tóm tắt bên phải
        update_summary_display()
        print(f"[Material DB] Recreated with: Air={air_name}, Mag={mag_type}, Iron={iron_type}")

    # --- 2. PHẦN BÊN TRÁI: CÀI ĐẶT VẬT LIỆU ---
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    
    # Tiêu đề
    header = QLabel("<h3>Global Material Settings</h3>")
    left_layout.addWidget(header)

    # Khung nhập liệu
    form_frame = QFrame()
    form_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 5px;")
    form_layout = QFormLayout(form_frame)
    form_layout.setContentsMargins(15, 15, 15, 15)
    form_layout.setSpacing(15)

    # A. Cài đặt không khí (Sử dụng bind_input cho relative_permeance)
    # Tuy nhiên bạn muốn gán tên/tính chất, ta dùng QLineEdit đơn giản cho tên trước
    input_tab.air_name_edit = QLineEdit("default")
    input_tab.air_name_edit.editingFinished.connect(update_global_database)
    form_layout.addRow("Air Medium Name:", input_tab.air_name_edit)

    # B. Chọn Nam châm (Dropdown)
    input_tab.mag_combo = QComboBox()
    input_tab.mag_combo.addItems(["N30UH", "N35SH", "N42SH"]) # Thêm các loại bạn sẽ định nghĩa
    input_tab.mag_combo.currentTextChanged.connect(update_global_database)
    form_layout.addRow("Magnet Grade:", input_tab.mag_combo)

    # C. Chọn Sắt (Dropdown)
    input_tab.iron_combo = QComboBox()
    input_tab.iron_combo.addItems(["M350-50A", "M400-50A", "M270-35A"])
    input_tab.iron_combo.currentTextChanged.connect(update_global_database)
    form_layout.addRow("Iron/Steel Core:", input_tab.iron_combo)

    left_layout.addWidget(form_frame)
    left_layout.addStretch()

    # --- 3. PHẦN BÊN PHẢI: TÓM TẮT THÔNG SỐ (PHẦN TRỐNG CHO ĐỒ THỊ SAU NÀY) ---
    right_container = QWidget()
    right_layout = QVBoxLayout(right_container)
    
    right_layout.addWidget(QLabel("<h3>Material Summary</h3>"))
    
    input_tab.summary_label = QLabel("Database not initialized.")
    input_tab.summary_label.setAlignment(Qt.AlignTop)
    input_tab.summary_label.setWordWrap(True)
    input_tab.summary_label.setStyleSheet("""
        background-color: #ffffff; 
        border: 2px dashed #bdc3c7; 
        padding: 20px; 
        font-family: 'Consolas', monospace;
    """)
    
    right_layout.addWidget(input_tab.summary_label)
    right_layout.addStretch()

    def update_summary_display():
        db = motor.material_database
        summary = (
            f"<b>AIR:</b> {db.air.name} (ur={db.air.relative_permeance})<br><br>"
            f"<b>MAGNET:</b> {db.magnet.name}<br>"
            f" - Mur: {db.magnet.relative_permeance}<br>"
            f" - Hc: {db.magnet.coercivity} A/m<br><br>"
            f"<b>IRON:</b> {db.iron.name}<br>"
            f" - B-H Data Points: {len(db.iron.B_H_curve['B_data'])} points"
        )
        input_tab.summary_label.setText(summary)

    # Thêm vào splitter
    splitter.addWidget(left_container)
    splitter.addWidget(right_container)
    splitter.setStretchFactor(1, 1) # Chia đều 2 bên
    
    main_layout.addWidget(splitter)

    # Khởi tạo database lần đầu khi mở giao diện
    update_global_database()
    
    return None