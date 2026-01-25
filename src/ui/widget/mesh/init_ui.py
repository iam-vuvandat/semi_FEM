import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QLabel, QPushButton, QScrollArea, QGroupBox, QProgressBar, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from pyvistaqt import QtInteractor
from src.ui.widget.widget.utils.bind_input import bind_input

class NetworkWorker(QThread):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, motor):
        super().__init__()
        self.motor = motor

    def run(self):
        try:
            self.motor.create_reluctance_network(callback=self.progress.emit)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

def init_ui(mesh_tab=None):
    if mesh_tab is None: return None

    motor = mesh_tab.main_window.motor
    mesh_data = motor.adaptive_mesh_data 
    
    main_layout = QHBoxLayout(mesh_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    splitter = QSplitter(Qt.Horizontal)

    # --- 1. LEFT PANEL: CONFIGURATION ---
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    left_layout.setContentsMargins(0, 0, 10, 0)
    left_layout.setSpacing(12)

    def on_generate_clicked():
        cur_motor = mesh_tab.main_window.motor
        mesh_tab.btn_generate.setEnabled(False)
        mesh_tab.progress_bar.setVisible(True)
        mesh_tab.worker = NetworkWorker(cur_motor)
        mesh_tab.worker.finished.connect(on_generation_finished)
        mesh_tab.worker.progress.connect(mesh_tab.progress_bar.setValue)
        mesh_tab.worker.start()

    def on_generation_finished():
        mesh_tab.btn_generate.setEnabled(True)
        mesh_tab.progress_bar.setVisible(False)
        on_refresh_clicked()

    def on_refresh_clicked():
        try:
            if mesh_tab is None: return
            cur_motor = mesh_tab.main_window.motor
            if cur_motor and cur_motor.reluctance_network and cur_motor.reluctance_network.elements is not None:
                mesh_tab.plotter.show()
                cur_motor.reluctance_network.display(plotter=mesh_tab.plotter)
                QApplication.processEvents()
                mesh_tab.plotter.render()
        except RuntimeError:
            pass

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    
    config_widget = QWidget()
    config_layout = QVBoxLayout(config_widget)
    config_layout.setSpacing(15)

    groups = {
        "logic":   create_classic_group("Mesh Logic _Flags"),
        "r_div":   create_classic_group("Radial Nodes (n r ...)"),
        "t_div":   create_classic_group("Tangential Nodes (n theta)"),
        "z_div":   create_classic_group("Axial Nodes (n z ...)"),
        "others":  create_classic_group("Other Parameters")
    }
    layouts = {key: gb.layout() for key, gb in groups.items()}

    for attr_name, value in vars(mesh_data).items():
        if attr_name.startswith('_'): continue
        display_name = attr_name.replace('n_', '').replace('_', ' ').title()
        
        unit_factor = 1 if attr_name.startswith('n_') else (1e3 if any(k in attr_name.lower() for k in ['dia', 'gap', 'length', 'width', 'opening', 'radius', 'ext']) else 1)
        
        if not attr_name.startswith('n_'):
            if 'arc' in attr_name.lower() or 'angle' in attr_name.lower(): display_name += " (Deg)"
            elif unit_factor == 1e3: display_name += " (mm)"
        
        input_widget = bind_input(mesh_data, attr_name, unit_factor, lambda: None)
        input_widget.setMinimumHeight(25)

        # Đảo thứ tự kiểm tra: Z trước, R sau để tránh trùng khớp "rotor" và "stator"
        if isinstance(value, bool): 
            layouts["logic"].addRow(f"{display_name}:", input_widget)
        elif 'z_' in attr_name: 
            layouts["z_div"].addRow(f"{display_name}:", input_widget)
        elif 'r_' in attr_name: 
            layouts["r_div"].addRow(f"{display_name}:", input_widget)
        elif 'theta' in attr_name: 
            layouts["t_div"].addRow(f"{display_name}:", input_widget)
        else: 
            layouts["others"].addRow(f"{display_name}:", input_widget)

    for key in ["logic", "r_div", "t_div", "z_div", "others"]:
        if layouts[key].rowCount() > 0: config_layout.addWidget(groups[key])
    
    config_layout.addStretch()
    scroll.setWidget(config_widget)
    left_layout.addWidget(scroll)

    mesh_tab.progress_bar = QProgressBar()
    mesh_tab.progress_bar.setFixedHeight(12)
    mesh_tab.progress_bar.setVisible(False)
    left_layout.addWidget(mesh_tab.progress_bar)

    mesh_tab.btn_generate = QPushButton("Update Reluctance Network Mesh")
    mesh_tab.btn_generate.setFixedHeight(45)
    mesh_tab.btn_generate.setStyleSheet("font-weight: bold; font-size: 13px;")
    mesh_tab.btn_generate.clicked.connect(on_generate_clicked)
    left_layout.addWidget(mesh_tab.btn_generate)

    right_container = QFrame()
    right_layout = QVBoxLayout(right_container)
    right_layout.setContentsMargins(0, 0, 0, 0)

    mesh_tab.plotter = QtInteractor(right_container)
    mesh_tab.plotter.set_background("white")
    mesh_tab.plotter.setMinimumSize(400, 400)
    right_layout.addWidget(mesh_tab.plotter)

    splitter.addWidget(left_container)
    splitter.addWidget(right_container)
    splitter.setStretchFactor(0, 1) 
    splitter.setStretchFactor(1, 2)
    main_layout.addWidget(splitter)
    
    QTimer.singleShot(1000, on_refresh_clicked)

    return None

def create_classic_group(title):
    group = QGroupBox(title)
    layout = QFormLayout(group)
    layout.setVerticalSpacing(12) 
    layout.setHorizontalSpacing(25)
    layout.setContentsMargins(15, 20, 15, 15)
    group.setStyleSheet("""
        QGroupBox { 
            font-weight: bold; 
            color: #333;
            border: 1px solid #ccd1d1; 
            border-radius: 4px;
            margin-top: 15px; 
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
        }
    """)
    return group