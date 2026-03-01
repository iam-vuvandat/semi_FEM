import sys
import os
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QLabel, QScrollArea, QGroupBox, QApplication)
from PyQt5.QtCore import Qt, QTimer
from pyvistaqt import QtInteractor
from src.ui.widget.widget.utils.bind_input import bind_input

# --- 1. HELPER FUNCTIONS ---
def create_classic_group(title):
    group = QGroupBox(title)
    layout = QFormLayout(group)
    layout.setVerticalSpacing(12) 
    layout.setHorizontalSpacing(25)
    layout.setContentsMargins(15, 20, 15, 15)
    group.setStyleSheet("""
        QGroupBox { 
            font-weight: bold; color: #333;
            border: 1px solid #ccd1d1; border-radius: 4px;
            margin-top: 15px; 
        }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
    """)
    return group

# --- 2. MAIN UI INITIALIZATION ---
def init_ui(mesh_tab=None):
    if mesh_tab is None: return None

    main_win = mesh_tab.main_window
    motor = main_win.motor
    mesh_data = motor.adaptive_mesh_data 
    
    main_layout = QHBoxLayout(mesh_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    splitter = QSplitter(Qt.Horizontal)

    # --- INTERNAL LOGIC FUNCTIONS ---

    def on_redraw():
        """Chỉ thực hiện vẽ Mesh hiện có trong RAM lên Plotter."""
        if hasattr(motor, 'mesh') and motor.mesh is not None:
            mesh_tab.plotter.clear()
            motor.mesh.show(
                plotter=mesh_tab.plotter,
                show_edges=True,
                opacity=0.3
            )
            mesh_tab.plotter.view_xy()
            mesh_tab.plotter.reset_camera()
            mesh_tab.plotter.render()

    def handle_refresh():
        """
        Hàm refresh thông minh cho việc chuyển Tab:
        Chỉ thực hiện chia lưới lại nếu StateManager báo dữ liệu đã lỗi thời.
        """
        if motor is None: return
        motor.require("mesh")
        on_redraw()
        QApplication.processEvents()

    def on_input_changed():
        """
        Callback khi người dùng sửa thông số trực tiếp tại tab Mesh:
        Hạ cờ Mesh và thực hiện tính toán lại ngay lập tức.
        """
        if motor is None: return
        motor.just_changed("mesh")
        handle_refresh()

    # Gán vào đối tượng tab để hỗ trợ cơ chế Smart Refresh từ Widget cha
    mesh_tab.refresh = handle_refresh
    mesh_tab.refresh_content = on_redraw

    # --- UI LAYOUT CONSTRUCTION (LEFT PANEL) ---
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    left_layout.setContentsMargins(0, 0, 10, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    
    config_widget = QWidget()
    config_layout = QVBoxLayout(config_widget)

    groups = {
        "logic":   create_classic_group("Mesh Logic Flags"),
        "r_div":   create_classic_group("Radial Nodes"),
        "t_div":   create_classic_group("Tangential Nodes"),
        "z_div":   create_classic_group("Axial Nodes"),
        "others":  create_classic_group("Other Parameters")
    }
    layouts = {key: gb.layout() for key, gb in groups.items()}

    for attr_name, value in vars(mesh_data).items():
        if attr_name.startswith('_'): continue
        
        display_name = attr_name.replace('n_', '').replace('_', ' ').title()
        is_node_count = attr_name.startswith('n_')
        unit_factor = 1.0 if is_node_count else 1000.0
        
        if not is_node_count:
            if 'arc' in attr_name.lower() or 'angle' in attr_name.lower(): display_name += " (°)"
            elif unit_factor == 1000.0: display_name += " (mm)"

        input_widget = bind_input(
            motor=mesh_data, 
            attr_name=attr_name, 
            unit_factor=unit_factor, 
            callback=on_input_changed
        )

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
        if layouts[key].rowCount() > 0: 
            config_layout.addWidget(groups[key])
    
    config_layout.addStretch()
    scroll.setWidget(config_widget)
    left_layout.addWidget(scroll)

    # --- RIGHT PANEL: 3D MESH PLOTTER ---
    right_container = QFrame()
    right_layout = QVBoxLayout(right_container)
    right_layout.setContentsMargins(0, 0, 0, 0)

    mesh_tab.plotter = QtInteractor(right_container)
    mesh_tab.plotter.set_background("white")
    right_layout.addWidget(mesh_tab.plotter)

    splitter.addWidget(left_container)
    splitter.addWidget(right_container)
    splitter.setStretchFactor(0, 1) 
    splitter.setStretchFactor(1, 2)
    main_layout.addWidget(splitter)
    
    QTimer.singleShot(500, handle_refresh)

    return None