import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QPushButton, QLabel, QApplication)
from PyQt5.QtCore import Qt
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(calculation_tab):
    if calculation_tab is None:
        return None

    main_win = calculation_tab.main_window
    motor = main_win.motor    
    calc_data = motor.calculation_data
    drive_data = motor.drive_data 
    
    def handle_refresh():
        if motor is None:
            return
        if not motor.motor_state_manager.ready_state.mesh:
            motor.require("mesh")
        if calculation_tab.status_label:
            calculation_tab.status_label.setText("Status: Ready (Dependencies satisfied)")
        QApplication.processEvents()

    def on_calc_changed():
        motor.just_changed("calculation_data")

    def on_drive_changed():
        motor.just_changed("drive")

    calculation_tab.refresh = handle_refresh

    main_layout = QVBoxLayout(calculation_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(5)

    content_splitter = QSplitter(Qt.Horizontal)

    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0, 0, 10, 0)

    form_widget = QWidget()
    form = QFormLayout(form_widget)
    form.setSpacing(10)
    
    solver_header = QLabel("Solver Settings")
    form.addRow(solver_header)

    conv_data = getattr(calc_data, "convergence_settings", None)
    if conv_data is not None:
        conv_inputs = [
            ("max_iteration", "Max Iteration:"),
            ("max_relative_residual", "Max Relative Residual:"),
            ("material_relax", "Material Relax:")
        ]
        for attr, label_text in conv_inputs:
            if hasattr(conv_data, attr):
                input_w = bind_input(
                    motor=conv_data, 
                    attr_name=attr, 
                    unit_factor=1.0, 
                    callback=on_calc_changed
                )
                if not isinstance(getattr(conv_data, attr), bool):
                    input_w.setFixedWidth(120)
                form.addRow(QLabel(label_text), input_w)

    gen_data = getattr(calc_data, "general_options", None)
    if gen_data is not None:
        gen_inputs = [
            ("n_point", "Points:"),
            ("solve_under_no_load", "Solve Under No Load:"),
            ("solve_on_load", "Solve On Load:"),
            ("solve_cogging", "Solve Cogging:"),
            ("solve_only_1_step", "Solve Only 1 Step:")
        ]
        for attr, label_text in gen_inputs:
            if hasattr(gen_data, attr):
                input_w = bind_input(
                    motor=gen_data, 
                    attr_name=attr, 
                    unit_factor=1.0, 
                    callback=on_calc_changed
                )
                if not isinstance(getattr(gen_data, attr), bool):
                    input_w.setFixedWidth(120)
                form.addRow(QLabel(label_text), input_w)

    drive_header = QLabel("Drive Settings")
    form.addRow(drive_header)

    line_i_rms = bind_input(drive_data, "i_rms", 1.0, on_drive_changed)
    line_i_rms.setFixedWidth(120)
    form.addRow(QLabel("I_rms (A):"), line_i_rms)

    line_phase = bind_input(drive_data, "phase_advanced", 1.0, on_drive_changed)
    line_phase.setFixedWidth(120)
    form.addRow(QLabel("Phase Advanced (degree):"), line_phase)

    left_layout.addWidget(form_widget)
    
    buttons_layout = QVBoxLayout()
    buttons_layout.setSpacing(8)
    
    calculation_tab.btn_run = QPushButton("Run Solver")
    calculation_tab.btn_run.setFixedHeight(35)
    
    calculation_tab.btn_cancel = QPushButton("Cancel")
    calculation_tab.btn_cancel.setObjectName("secondaryButton")
    calculation_tab.btn_cancel.setFixedHeight(30)
    calculation_tab.btn_cancel.setEnabled(False) 
    
    buttons_layout.addWidget(calculation_tab.btn_run)
    buttons_layout.addWidget(calculation_tab.btn_cancel)
    
    left_layout.addLayout(buttons_layout)
    left_layout.addStretch()

    calculation_tab.viz_container = QFrame()
    calculation_tab.viz_container.setFrameShape(QFrame.StyledPanel)
    
    calculation_tab.viz_layout = QVBoxLayout(calculation_tab.viz_container)
    calculation_tab.viz_layout.setContentsMargins(0, 0, 0, 0)
    
    log_label = QLabel("Solver Visualization / Log Area")
    log_label.setAlignment(Qt.AlignCenter)
    calculation_tab.viz_layout.addWidget(log_label)

    content_splitter.addWidget(left_widget)
    content_splitter.addWidget(calculation_tab.viz_container)
    content_splitter.setStretchFactor(1, 4) 

    main_layout.addWidget(content_splitter, 1)

    status_container = QFrame()
    status_container.setFixedHeight(35)
    status_layout = QHBoxLayout(status_container)
    status_layout.setContentsMargins(15, 0, 15, 0)

    calculation_tab.status_label = QLabel("Status: Ready")
    status_layout.addWidget(calculation_tab.status_label)
    status_layout.addStretch()

    main_layout.addWidget(status_container, 0)
    
    return None