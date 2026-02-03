import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QPushButton, QLabel, QTextEdit, QProgressBar, QCheckBox)
from PyQt5.QtCore import Qt
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(calculation_tab):
    motor = calculation_tab.main_window.motor
    if not hasattr(motor, 'calculation_data'):
        motor.create_calculation_data()
    
    calc_data = motor.calculation_data
    
    main_layout = QHBoxLayout(calculation_tab)
    splitter = QSplitter(Qt.Horizontal)

    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)

    input_frame = QFrame()
    input_frame.setStyleSheet("background-color: white; border: 1px solid #dee2e6; border-radius: 4px;")
    form = QFormLayout(input_frame)

    # Danh sach tham so day du
    inputs = [
        ("max_relative_residual", "Max Relative Residual"),
        ("max_iteration", "Max Iteration"),
        ("material_relax", "Material Relax"),
        ("n_point", "Number of Points")
    ]

    for attr, label in inputs:
        if hasattr(calc_data, attr):
            form.addRow(f"{label}:", bind_input(calc_data, attr, 1, lambda: None))

    calculation_tab.check_cogging = QCheckBox("Solve Cogging")
    calculation_tab.check_cogging.setChecked(getattr(calc_data, "solve_cogging", True))
    calculation_tab.check_cogging.stateChanged.connect(lambda v: setattr(calc_data, "solve_cogging", bool(v)))
    form.addRow(calculation_tab.check_cogging)

    calculation_tab.check_debug = QCheckBox("Debug Mode")
    calculation_tab.check_debug.setChecked(getattr(calc_data, "debug", True))
    calculation_tab.check_debug.stateChanged.connect(lambda v: setattr(calc_data, "debug", bool(v)))
    form.addRow(calculation_tab.check_debug)

    left_layout.addWidget(QLabel("<b>Solver Settings</b>"))
    left_layout.addWidget(input_frame)

    calculation_tab.btn_run = QPushButton("Run 3D-MBGRN Solver")
    calculation_tab.btn_run.setStyleSheet("""
        QPushButton { background-color: #1976D2; color: white; font-weight: bold; padding: 12px; border-radius: 4px; margin-top: 10px; }
        QPushButton:hover { background-color: #1565C0; }
    """)
    calculation_tab.btn_run.clicked.connect(calculation_tab.run_solver)
    
    left_layout.addWidget(calculation_tab.btn_run)
    left_layout.addStretch()

    right_panel = QWidget()
    right_layout = QVBoxLayout(right_panel)
    
    calculation_tab.progress_bar = QProgressBar()
    calculation_tab.progress_bar.setValue(0)
    
    calculation_tab.log_console = QTextEdit()
    calculation_tab.log_console.setReadOnly(True)
    calculation_tab.log_console.setStyleSheet("background-color: #1E1E1E; color: #D4D4D4; font-family: 'Consolas'; font-size: 11pt;")

    right_layout.addWidget(QLabel("<b>Solver Progress</b>"))
    right_layout.addWidget(calculation_tab.progress_bar)
    right_layout.addWidget(QLabel("<b>Analysis Logs</b>"))
    right_layout.addWidget(calculation_tab.log_console)

    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setStretchFactor(1, 2)
    main_layout.addWidget(splitter)