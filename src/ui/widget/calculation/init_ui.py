import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QPushButton, QLabel, QCheckBox, QApplication)
from PyQt5.QtCore import Qt
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(calculation_tab):
    if calculation_tab is None: return None

    main_win = calculation_tab.main_window
    motor = main_win.motor    
    calc_data = motor.calculation_data
    drive_data = motor.drive_data 
    
    # --- HÀM CẬP NHẬT TRẠNG THÁI (SMART REFRESH) ---
    
    def handle_refresh():
        """
        Kiểm tra trạng thái lỗi thời của toàn bộ chuỗi dữ liệu trước đó.
        Yêu cầu Mesh phải 'tươi' trước khi cho phép Calculation hoạt động.
        """
        if motor is None: return
        # require("mesh") sẽ kéo theo require của Material, Geometry và Winding
        motor.require("mesh")
        if calculation_tab.status_label:
            calculation_tab.status_label.setText("Status: Ready (Dependencies satisfied)")
        QApplication.processEvents()

    def on_calc_changed():
        """Báo cho Manager rằng thông số giải thuật đã đổi."""
        motor.just_changed("calculation_data")

    def on_drive_changed():
        """Báo cho Manager rằng hằng số dòng điện đã đổi."""
        motor.just_changed("drive")

    # Gán vào đối tượng tab để class cha (Widget) có thể gọi tự động khi chuyển tab
    calculation_tab.refresh = handle_refresh

    # --- LAYOUT CHÍNH ---
    main_layout = QVBoxLayout(calculation_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(5)

    content_splitter = QSplitter(Qt.Horizontal)

    # --- PANEL TRÁI: CÀI ĐẶT ---
    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0, 0, 10, 0)

    form_widget = QWidget()
    form = QFormLayout(form_widget)
    form.setSpacing(10)
    
    # 1. SOLVER SETTINGS
    solver_header = QLabel("⚙️ Solver Settings")
    solver_header.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50; margin-bottom: 5px;")
    form.addRow(solver_header)

    solver_inputs = [
        ("max_relative_residual", "Max Residual:"),
        ("max_iteration", "Max Iter:"),
        ("material_relax", "Material Relax:"),
        ("n_point", "Points:"),
        ("solve_cogging", "Solve Cogging Torque:"),
        ("get_geometric_error", "Get Geometric Error:"),
        ("solve_only_1_step", "Solve Only 1 Step:"),
        ("debug", "Debug Mode (Verbose):")
    ]

    for attr, label_text in solver_inputs:
        if hasattr(calc_data, attr):
            input_w = bind_input(
                motor = calc_data, 
                attr_name = attr, 
                unit_factor = 1.0, 
                callback = on_calc_changed
            )
            if not isinstance(getattr(calc_data, attr), bool):
                input_w.setFixedWidth(120)
            form.addRow(QLabel(label_text), input_w)

    # 2. DRIVE SETTINGS
    drive_header = QLabel("⚡ Drive Settings")
    drive_header.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50; margin-top: 15px; margin-bottom: 5px;")
    form.addRow(drive_header)

    line_i_rms = bind_input(drive_data, "i_rms", 1.0, on_drive_changed)
    line_i_rms.setFixedWidth(120)
    form.addRow(QLabel("$I_{rms}$ (A):"), line_i_rms)

    line_phase = bind_input(drive_data, "phase_advanced", 1.0, on_drive_changed)
    line_phase.setFixedWidth(120)
    form.addRow(QLabel("Phase Advanced (°):"), line_phase)

    left_layout.addWidget(form_widget)
    
    # --- NÚT BẤM ĐIỀU KHIỂN ---
    buttons_layout = QVBoxLayout()
    buttons_layout.setSpacing(8)
    
    calculation_tab.btn_run = QPushButton("🚀 Run Solver")
    calculation_tab.btn_run.setFixedHeight(40)
    calculation_tab.btn_run.setStyleSheet("""
        QPushButton { font-weight: bold; background-color: #2ecc71; color: white; border-radius: 5px; }
        QPushButton:hover { background-color: #27ae60; }
    """)
    
    # Kết nối logic Run từ class Calculation (Sẽ gọi thông qua tab tham chiếu)
    # Lưu ý: Kết nối thực tế sẽ được class Calculation thực hiện sau khi init_ui xong

    calculation_tab.btn_cancel = QPushButton("Cancel")
    calculation_tab.btn_cancel.setFixedHeight(30)
    calculation_tab.btn_cancel.setEnabled(False) 
    
    buttons_layout.addWidget(calculation_tab.btn_run)
    buttons_layout.addWidget(calculation_tab.btn_cancel)
    
    left_layout.addLayout(buttons_layout)
    left_layout.addStretch()

    # --- PANEL PHẢI: VIZ & LOG ---
    calculation_tab.viz_container = QFrame()
    calculation_tab.viz_container.setFrameShape(QFrame.StyledPanel)
    calculation_tab.viz_container.setStyleSheet("background-color: #ffffff; border: 1px solid #dcdcdc; border-radius: 4px;")
    
    calculation_tab.viz_layout = QVBoxLayout(calculation_tab.viz_container)
    
    log_label = QLabel("Solver Visualization / Log Area")
    log_label.setAlignment(Qt.AlignCenter)
    log_label.setStyleSheet("color: #95a5a6; font-style: italic;")
    calculation_tab.viz_layout.addWidget(log_label)

    content_splitter.addWidget(left_widget)
    content_splitter.addWidget(calculation_tab.viz_container)
    content_splitter.setStretchFactor(1, 4) 

    main_layout.addWidget(content_splitter, 1)

    # --- STATUS BAR DƯỚI CÙNG ---
    status_container = QFrame()
    status_container.setFixedHeight(35)
    status_container.setStyleSheet("background-color: #ecf0f1; border-top: 1px solid #bdc3c7;")
    status_layout = QHBoxLayout(status_container)
    status_layout.setContentsMargins(15, 0, 15, 0)

    calculation_tab.status_label = QLabel("Status: Ready")
    calculation_tab.status_label.setStyleSheet("font-weight: bold; color: #34495e;")
    status_layout.addWidget(calculation_tab.status_label)
    status_layout.addStretch()

    main_layout.addWidget(status_container, 0)
    
    return None