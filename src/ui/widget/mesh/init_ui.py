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

    # Define groups following the new naming convention
    groups = {
        "logic":   create_classic_group("Mesh Logic & Flags"),
        "r_div":   create_classic_group("Radial Discretization (Nodes)"),
        "t_div":   create_classic_group("Tangential Discretization (Nodes)"),
        "z_div":   create_classic_group("Axial Discretization (Nodes)"),
        "others":  create_classic_group("Other Parameters")
    }

    layouts = {key: gb.layout() for key, gb in groups.items()}

    # Automatic sorting and binding based on new long-form names
    for attr_name, value in vars(mesh_data).items():
        if attr_name.startswith('_'): continue
        
        # Format label: 'nodes_axial_airgap' -> 'Axial Airgap'
        display_name = attr_name.replace('nodes_', '').replace('_', ' ').title()
        
        # Bind input (unit_factor=1 for discretization counts)
        input_widget = bind_input(
            motor=mesh_data, 
            attr_name=attr_name, 
            unit_factor=1, 
            callback=lambda: update_mesh_summary(mesh_tab, motor, mesh_data)
        )

        # Smart classification logic updated for new naming
        if isinstance(value, bool):
            layouts["logic"].addRow(f"{display_name}:", input_widget)
        elif 'radial' in attr_name:
            layouts["r_div"].addRow(f"{display_name}:", input_widget)
        elif 'tangential' in attr_name:
            layouts["t_div"].addRow(f"{display_name}:", input_widget)
        elif 'axial' in attr_name:
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
    
    # Summary Dashboard
    mesh_tab.summary_label = QLabel("Analyzing mesh structure...")
    mesh_tab.summary_label.setStyleSheet("font-family: 'Consolas', monospace; font-size: 10pt; background: #fff; border: 1px solid #ddd; padding: 10px;")
    right_layout.addWidget(mesh_tab.summary_label)

    # 3D Viewport
    mesh_tab.plot_area = QFrame()
    mesh_tab.plot_area.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
    mesh_tab.plot_area.setStyleSheet("background-color: #f0f0f0;")
    
    right_layout.addWidget(mesh_tab.plot_area, stretch=1)

    # Action Button
    mesh_tab.btn_generate = QPushButton("Update Reluctance Network Mesh")
    mesh_tab.btn_generate.setFixedHeight(35)
    mesh_tab.btn_generate.setStyleSheet("font-weight: bold;")
    mesh_tab.btn_generate.clicked.connect(motor.create_adaptive_mesh)
    right_layout.addWidget(mesh_tab.btn_generate)

    splitter.addWidget(left_container)
    splitter.addWidget(right_container)
    splitter.setStretchFactor(0, 1) 
    splitter.setStretchFactor(1, 3) 
    
    main_layout.addWidget(splitter)
    
    update_mesh_summary(mesh_tab, motor, mesh_data)
    return None

def create_classic_group(title):
    group = QGroupBox(title)
    layout = QFormLayout(group)
    layout.setLabelAlignment(Qt.AlignLeft)
    group.setStyleSheet("QGroupBox { font-weight: bold; color: #2c3e50; }")
    return group

def update_mesh_summary(tab, motor, data):
    """Calculates node counts using the new naming convention"""
    try:
        attrs = vars(data)
        # Sum nodes in each direction using new 'nodes_' prefix
        nr = sum([v for k, v in attrs.items() if 'radial' in k and isinstance(v, int)])
        nz = sum([v for k, v in attrs.items() if 'axial' in k and isinstance(v, int)])
        nt = getattr(data, 'nodes_tangential_theta', 0)
        
        # Total nodes in a cylindrical mesh
        # Calculation: $N_{total} = (N_r + 1) \times (N_{\theta} + 1) \times (N_z + 1)$
        total_nodes = (nr + 1) * (nt + 1) * (nz + 1)
        
        info = (
            f"<b>3D MESH STATISTICS</b><br>"
            f"Symmetry Multiplier: {motor.symmetry_factor}<br>"
            f"Radial Nodes: {nr + 1}<br>"
            f"Tangential Nodes: {nt + 1}<br>"
            f"Axial Nodes: {nz + 1}<br>"
            f"--------------------------<br>"
            f"<b style='color: #e67e22;'>Total Nodes: {total_nodes:,}</b>"
        )
        tab.summary_label.setText(info)
    except Exception as e:
        tab.summary_label.setText(f"Error: {str(e)}")