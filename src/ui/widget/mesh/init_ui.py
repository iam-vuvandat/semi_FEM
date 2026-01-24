import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QLabel, QPushButton, QScrollArea, QGroupBox)
from PyQt5.QtCore import Qt
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(mesh_tab=None):
    if mesh_tab is None: return None

    motor = mesh_tab.main_window.motor
    mesh_data = motor.adaptive_mesh_data 
    
    main_layout = QHBoxLayout(mesh_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    # Splitter with 1:3 ratio
    splitter = QSplitter(Qt.Horizontal)

    # --- 1. LEFT PANEL: CONFIGURATION (Ratio 1) ---
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    left_layout.setContentsMargins(0, 0, 5, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    
    config_widget = QWidget()
    config_layout = QVBoxLayout(config_widget)
    config_layout.setSpacing(15)

    # Define groups following the classic style
    groups = {
        "logic":   create_classic_group("Mesh Logic & Flags"),
        "r_div":   create_classic_group("Radial Discretization (n_r)"),
        "t_div":   create_classic_group("Tangential Discretization (n_theta)"),
        "z_div":   create_classic_group("Axial Discretization (n_z)"),
        "others":  create_classic_group("Other Parameters")
    }

    # Map for layouts
    layouts = {key: gb.layout() for key, gb in groups.items()}

    # Automatic sorting and binding
    for attr_name, value in vars(mesh_data).items():
        if attr_name.startswith('_'): continue
        
        # Format label: 'n_z_airgap' -> 'Z Airgap'
        display_name = attr_name.replace('n_', '').replace('_', ' ').title()
        
        # Use bind_input (unit_factor=1 for divisions)
        # Note: bind_input returns the QLineEdit or QCheckBox
        input_widget = bind_input(
            motor=mesh_data, 
            attr_name=attr_name, 
            unit_factor=1, 
            callback=lambda: update_mesh_summary(mesh_tab, motor, mesh_data)
        )

        # Smart classification
        if isinstance(value, bool):
            layouts["logic"].addRow(f"{display_name}:", input_widget)
        elif attr_name.startswith('n_r'):
            layouts["r_div"].addRow(f"{display_name}:", input_widget)
        elif attr_name.startswith('n_theta'):
            layouts["t_div"].addRow(f"{display_name}:", input_widget)
        elif attr_name.startswith('n_z'):
            layouts["z_div"].addRow(f"{display_name}:", input_widget)
        else:
            layouts["others"].addRow(f"{display_name}:", input_widget)

    # Add non-empty groups to the layout
    for key in ["logic", "r_div", "t_div", "z_div", "others"]:
        if layouts[key].rowCount() > 0:
            config_layout.addWidget(groups[key])

    config_layout.addStretch()
    scroll.setWidget(config_widget)
    left_layout.addWidget(scroll)

    # --- 2. RIGHT PANEL: DASHBOARD & VIEW (Ratio 3) ---
    right_container = QFrame()
    right_layout = QVBoxLayout(right_container)
    
    # Info Label (Classic text style)
    mesh_tab.summary_label = QLabel("Mesh statistics will appear here...")
    mesh_tab.summary_label.setAlignment(Qt.AlignTop)
    mesh_tab.summary_label.setStyleSheet("font-family: 'Segoe UI'; font-size: 10pt; color: #333;")
    right_layout.addWidget(mesh_tab.summary_label)

    # Placeholder for the 3D Plotter
    mesh_tab.plot_area = QFrame()
    mesh_tab.plot_area.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
    mesh_tab.plot_area.setStyleSheet("background-color: #f0f0f0;") # Classic light gray
    plot_layout = QVBoxLayout(mesh_tab.plot_area)
    plot_layout.addWidget(QLabel("3D MESH VIEWPORT", alignment=Qt.AlignCenter))
    
    right_layout.addWidget(mesh_tab.plot_area, stretch=1)

    # Manual mesh generation button (Classic style)
    mesh_tab.btn_generate = QPushButton("Generate Reluctance Network")
    mesh_tab.btn_generate.setFixedHeight(30)
    mesh_tab.btn_generate.clicked.connect(motor.create_adaptive_mesh)
    right_layout.addWidget(mesh_tab.btn_generate)

    # Set up Splitter
    splitter.addWidget(left_container)
    splitter.addWidget(right_container)
    splitter.setStretchFactor(0, 1) # Ratio 1
    splitter.setStretchFactor(1, 3) # Ratio 3
    
    main_layout.addWidget(splitter)
    
    # Initial summary update
    update_mesh_summary(mesh_tab, motor, mesh_data)

    return None

def create_classic_group(title):
    """Helper to create a GroupBox with a bold centered title similar to Geometry tab"""
    group = QGroupBox()
    layout = QFormLayout(group)
    layout.setLabelAlignment(Qt.AlignLeft)
    layout.setFormAlignment(Qt.AlignTop)
    
    # Customizing GroupBox title appearance to match Geometry tab "Radial Parameters"
    group.setTitle(title)
    group.setStyleSheet("QGroupBox { font-weight: bold; }")
    return group

def update_mesh_summary(tab, motor, data):
    """Update statistics on the right panel"""
    try:
        attrs = vars(data)
        nr = sum([v for k, v in attrs.items() if k.startswith('n_r') and isinstance(v, int)])
        nz = sum([v for k, v in attrs.items() if k.startswith('n_z') and isinstance(v, int)])
        nt = getattr(data, 'n_theta', 0)
        
        total = (nr + 1) * (nt + 1) * (nz + 1)
        
        info = (
            f"<b>MESH ANALYSIS</b><br>"
            f"Symmetry Factor: {motor.symmetry_factor}<br>"
            f"Radial Nodes: {nr + 1}<br>"
            f"Tangential Nodes: {nt + 1}<br>"
            f"Axial Nodes: {nz + 1}<br>"
            f"--------------------------<br>"
            f"<b>Total Nodes: {total:,}</b>"
        )
        tab.summary_label.setText(info)
    except:
        tab.summary_label.setText("Error calculating mesh statistics.")