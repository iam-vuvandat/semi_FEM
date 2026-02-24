import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QPushButton, QLabel, QCheckBox)
from PyQt5.QtCore import Qt
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(calculation_tab):
    motor = calculation_tab.main_window.motor
    
    # Đảm bảo các đối tượng dữ liệu tồn tại
    if not hasattr(motor, 'calculation_data'):
        motor.create_calculation_data()
    
    # Khởi tạo Drive nếu chưa có (tùy thuộc vào cấu trúc motor của bạn)
    if not hasattr(motor, 'drive'):
        from src.core.drive.drive_class import Drive # Giả định đường dẫn class Drive
        motor.drive = Drive(motor)
        
    calc_data = motor.calculation_data
    drive = motor.drive
    
    main_layout = QVBoxLayout(calculation_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(5)

    content_splitter = QSplitter(Qt.Horizontal)

    # --- LEFT PANEL: SETTINGS ---
    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0, 0, 10, 0)

    form_widget = QWidget()
    form = QFormLayout(form_widget)
    form.setLabelAlignment(Qt.AlignLeft)
    form.setFormAlignment(Qt.AlignLeft)
    form.setSpacing(10)
    
    # 1. --- SECTION: SOLVER SETTINGS ---
    solver_header = QLabel("Solver Settings")
    solver_header.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 5px;")
    form.addRow(solver_header)

    solver_inputs = [
        ("max_relative_residual", "Max Residual:"),
        ("max_iteration", "Max Iter:"),
        ("material_relax", "Material Relax:"),
        ("n_point", "Points:"),
        ("solve_cogging", "Solve Cogging Torque:"),
        ("debug", "Debug Mode (Verbose):")
    ]

    for attr, label_text in solver_inputs:
        if hasattr(calc_data, attr):
            current_val = getattr(calc_data, attr)
            if isinstance(current_val, bool):
                checkbox = QCheckBox()
                checkbox.setChecked(current_val)
                checkbox.stateChanged.connect(lambda state, a=attr: setattr(calc_data, a, state == Qt.Checked))
                form.addRow(QLabel(label_text), checkbox)
                setattr(calculation_tab, f"check_{attr}", checkbox)
            else:
                line_edit = bind_input(calc_data, attr, 1, lambda: None)
                line_edit.setFixedWidth(120)
                form.addRow(QLabel(label_text), line_edit)

    # 2. --- SECTION: DRIVE SETTINGS ---
    drive_header = QLabel("Drive Settings")
    drive_header.setStyleSheet("font-weight: bold; font-size: 14px; margin-top: 15px; margin-bottom: 5px;")
    form.addRow(drive_header)

    # Hàm cập nhật lại id, iq mỗi khi I_rms hoặc Phase_advanced thay đổi
    def update_drive_logic():
        drive.set_control(drive.i_rms, drive.phase_advanced)

    # Nhập I rms
    line_i_rms = bind_input(drive, "i_rms", 1, update_drive_logic)
    line_i_rms.setFixedWidth(120)
    form.addRow(QLabel("I rms (A):"), line_i_rms)

    # Nhập Phase Advanced
    line_phase = bind_input(drive, "phase_advanced", 1, update_drive_logic)
    line_phase.setFixedWidth(120)
    form.addRow(QLabel("Phase Advanced (deg):"), line_phase)

    left_layout.addWidget(form_widget)
    
    # Nút chạy Solver
    calculation_tab.btn_run = QPushButton("Run Solver")
    calculation_tab.btn_run.setFixedHeight(30)
    calculation_tab.btn_run.clicked.connect(calculation_tab.run_solver)
    left_layout.addWidget(calculation_tab.btn_run)
    
    left_layout.addStretch()

    # --- RIGHT PANEL: 3D VIEW ---
    calculation_tab.viz_container = QFrame()
    calculation_tab.viz_container.setFrameShape(QFrame.StyledPanel)
    calculation_tab.viz_container.setStyleSheet("background-color: #ffffff; border: 1px solid #dcdcdc;")
    
    calculation_tab.viz_layout = QVBoxLayout(calculation_tab.viz_container)
    calculation_tab.viz_layout.setContentsMargins(0, 0, 0, 0)
    calculation_tab.viz_layout.setSpacing(0)

    content_splitter.addWidget(left_widget)
    content_splitter.addWidget(calculation_tab.viz_container)
    content_splitter.setStretchFactor(1, 4) 

    main_layout.addWidget(content_splitter, 1)

    # --- BOTTOM: STATUS BAR ---
    status_container = QFrame()
    status_container.setFixedHeight(30)
    status_container.setStyleSheet("background-color: #f8f8f8; border-top: 1px solid #dcdcdc;")
    status_layout = QHBoxLayout(status_container)
    status_layout.setContentsMargins(10, 0, 10, 0)

    calculation_tab.status_label = QLabel("Status: Ready")
    calculation_tab.status_label.setStyleSheet("font-size: 13px; color: #333;")
    status_layout.addWidget(calculation_tab.status_label)
    status_layout.addStretch()

    main_layout.addWidget(status_container, 0)