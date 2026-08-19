import numpy as np
import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QScrollArea, QGroupBox, QPushButton, QLabel, QTextEdit, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from pyvistaqt import QtInteractor
from src.ui.widget.widget.utils.bind_input import bind_input

def create_classic_group(title):
    group = QGroupBox(title)
    layout = QFormLayout(group)
    layout.setVerticalSpacing(12) 
    layout.setHorizontalSpacing(25)
    layout.setContentsMargins(15, 20, 15, 15)
    return group

def format_attr_value(val):
    if val is None:
        return "None"
    if isinstance(val, (bool, str)):
        return str(val)
    if isinstance(val, (int, np.integer)):
        return str(val)
    if isinstance(val, (float, np.floating)):
        return f"{val:.6g}"
    if isinstance(val, np.ndarray):
        if val.size == 0:
            return "[]"
        if val.ndim <= 2:
            return np.array2string(np.round(val, 6), precision=4, separator=', ', suppress_small=True)
        return f"array shape {val.shape}"
    if isinstance(val, (list, tuple)):
        return str([format_attr_value(x) for x in val])
    return str(val)

def init_ui(mesh_tab=None):
    if mesh_tab is None:
        return None

    main_win = mesh_tab.main_window
    motor = main_win.motor
    mesh_data = motor.adaptive_mesh_data 
    
    mesh_tab.current_view_mode = "mesh"
    mesh_tab.current_pyvista_grid = None
    mesh_tab.curr_i = 0
    mesh_tab.curr_j = 0
    mesh_tab.curr_k = 0
    
    main_layout = QVBoxLayout(mesh_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(5)

    content_splitter = QSplitter(Qt.Horizontal)

    def update_element_inspector(i, j, k):
        if not hasattr(motor, 'reluctance_network') or motor.reluctance_network is None:
            mesh_tab.debug_info_box.setText("No Reluctance Network data available.\nPlease switch to Material View to discretize.")
            return
        
        elements_3d = motor.reluctance_network.elements
        if elements_3d is None:
            mesh_tab.debug_info_box.setText("Elements matrix is not created.")
            return
            
        ni, nj, nk = elements_3d.shape
        mesh_tab.curr_i = int(np.clip(i, 0, ni - 1))
        mesh_tab.curr_j = int(j % nj)
        mesh_tab.curr_k = int(np.clip(k, 0, nk - 1))

        mesh_tab.pos_label.setText(f"Index: [{mesh_tab.curr_i}, {mesh_tab.curr_j}, {mesh_tab.curr_k}]")
        
        el = elements_3d[mesh_tab.curr_i, mesh_tab.curr_j, mesh_tab.curr_k]
        if el is None:
            mesh_tab.debug_info_box.setText(f"Position [{mesh_tab.curr_i}, {mesh_tab.curr_j}, {mesh_tab.curr_k}]: None")
            return

        vol = el.get_volume() * 1e9 if hasattr(el, 'get_volume') and callable(el.get_volume) else None

        lines = [
            "ELEMENT PROPERTIES",
            f"Index Position               : [{mesh_tab.curr_i}, {mesh_tab.curr_j}, {mesh_tab.curr_k}]",
            f"Flat Position                : {format_attr_value(getattr(el, 'flat_position', None))}",
            f"Material                     : {format_attr_value(getattr(el, 'material', 'Not Available'))}",
            f"Volume (cubic millimeter)    : {format_attr_value(vol)}",
            "----------------------------------------",
            f"Length (meter)               : {format_attr_value(getattr(el, 'length', None))}",
            f"Section Area (square meter)  : {format_attr_value(getattr(el, 'section_area', None))}",
            f"Reluctance                   : {format_attr_value(getattr(el, 'reluctance', None))}",
            f"Vacuum Reluctance            : {format_attr_value(getattr(el, 'vacuum_reluctance', None))}",
            f"Minimum Reluctance           : {format_attr_value(getattr(el, 'minimum_reluctance', None))}",
            f"Relative Permeability        : {format_attr_value(getattr(el, 'relative_permeability', None))}",
            f"Average Flux Density         : {format_attr_value(getattr(el, 'flux_density_average', None))}",
            f"Directional Flux Density     : {format_attr_value(getattr(el, 'flux_density_direct', None))}",
            f"Magnetic Potential           : {format_attr_value(getattr(el, 'own_magnetic_potential', None))}",
            f"Permanent Magnet Source      : {format_attr_value(getattr(el, 'magnet_source', None))}",
            f"Winding Current Source       : {format_attr_value(getattr(el, 'winding_source', None))}",
            f"Total Magnetic Source        : {format_attr_value(getattr(el, 'magnetic_source', None))}"
        ]
        mesh_tab.debug_info_box.setText("\n".join(lines))

        if mesh_tab.current_pyvista_grid is not None:
            idx = mesh_tab.curr_i + mesh_tab.curr_j * ni + mesh_tab.curr_k * ni * nj
            try:
                selected_cell = mesh_tab.current_pyvista_grid.extract_cells([idx])
                mesh_tab.plotter.add_mesh(selected_cell, color="#F1C40F", opacity=0.8, name="debug_highlight_box")
                mesh_tab.plotter.add_mesh(selected_cell, color="#E74C3C", style='wireframe', line_width=4, name="debug_highlight_wire")
            except Exception:
                pass

    def on_cell_picked(cell):
        if cell is None or mesh_tab.current_view_mode != "material":
            return
        try:
            i = int(cell.cell_data["idx_i"][0])
            j = int(cell.cell_data["idx_j"][0])
            k = int(cell.cell_data["idx_k"][0])
            update_element_inspector(i, j, k)
        except Exception:
            pass

    def move_inspector_idx(di, dj, dk):
        update_element_inspector(mesh_tab.curr_i + di, mesh_tab.curr_j + dj, mesh_tab.curr_k + dk)

    def on_redraw():
        if mesh_tab.plotter is None:
            return
            
        mesh_tab.plotter.clear()
        
        if mesh_tab.current_view_mode == "mesh":
            mesh_tab.inspector_panel.setVisible(False)
            if hasattr(motor, 'mesh') and motor.mesh is not None:
                motor.mesh.show(
                    plotter=mesh_tab.plotter,
                    show_edges=True,
                    opacity=0.3
                )
                mesh_tab.plotter.view_xy()
                mesh_tab.plotter.reset_camera()
        elif mesh_tab.current_view_mode == "material":
            mesh_tab.inspector_panel.setVisible(True)
            if hasattr(motor, 'reluctance_network') and motor.reluctance_network is not None:
                if hasattr(motor.reluctance_network, 'show_material'):
                    mesh_tab.current_pyvista_grid = motor.reluctance_network.show_material(plotter=mesh_tab.plotter)
                
                if mesh_tab.current_pyvista_grid is not None:
                    ni, nj, nk = motor.reluctance_network.elements.shape
                    idx_i, idx_j, idx_k = np.meshgrid(np.arange(ni), np.arange(nj), np.arange(nk), indexing='ij')
                    mesh_tab.current_pyvista_grid.cell_data["idx_i"] = idx_i.flatten(order='F')
                    mesh_tab.current_pyvista_grid.cell_data["idx_j"] = idx_j.flatten(order='F')
                    mesh_tab.current_pyvista_grid.cell_data["idx_k"] = idx_k.flatten(order='F')
                    
                    mesh_tab.plotter.enable_cell_picking(callback=on_cell_picked, show=False)
                    update_element_inspector(mesh_tab.curr_i, mesh_tab.curr_j, mesh_tab.curr_k)

                mesh_tab.plotter.view_xy()
                mesh_tab.plotter.reset_camera()
        
        mesh_tab.plotter.render()

    def handle_refresh():
        mesh_tab.refresh()

    def on_input_changed():
        if motor is None:
            return
        motor.just_changed("mesh")
        handle_refresh()

    def set_view_mode(mode):
        mesh_tab.current_view_mode = mode
        if mode == "mesh":
            mesh_tab.btn_mesh_view.setEnabled(False)
            mesh_tab.btn_material_view.setEnabled(True)
            mesh_tab.inspector_panel.setVisible(False)
            if not motor.motor_state_manager.ready_state.mesh:
                mesh_tab.run_require_async("mesh", on_redraw)
            else:
                on_redraw()
        else:
            mesh_tab.btn_mesh_view.setEnabled(True)
            mesh_tab.btn_material_view.setEnabled(False)
            mesh_tab.inspector_panel.setVisible(True)
            if not motor.motor_state_manager.ready_state.reluctance_network:
                mesh_tab.run_require_async("reluctance_network", on_redraw)
            else:
                on_redraw()

    mesh_tab.refresh_content = on_redraw

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
        if attr_name.startswith('_'):
            continue
        
        display_name = attr_name.replace('n_', '').replace('_', ' ').title()
        is_node_count = attr_name.startswith('n_')
        unit_factor = 1.0 if is_node_count else 1000.0
        
        if not is_node_count:
            if 'arc' in attr_name.lower() or 'angle' in attr_name.lower():
                display_name += " (degree)"
            elif unit_factor == 1000.0:
                display_name += " (mm)"

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

    right_container = QFrame()
    right_layout = QVBoxLayout(right_container)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.setSpacing(5)

    view_btn_layout = QHBoxLayout()
    view_btn_layout.setContentsMargins(0, 0, 0, 0)
    view_btn_layout.setSpacing(5)

    mesh_tab.btn_mesh_view = QPushButton("Switch to Mesh View")
    mesh_tab.btn_mesh_view.setEnabled(False)
    mesh_tab.btn_mesh_view.clicked.connect(lambda: set_view_mode("mesh"))

    mesh_tab.btn_material_view = QPushButton("Switch to Material View")
    mesh_tab.btn_material_view.clicked.connect(lambda: set_view_mode("material"))

    view_btn_layout.addWidget(mesh_tab.btn_mesh_view)
    view_btn_layout.addWidget(mesh_tab.btn_material_view)
    view_btn_layout.addStretch()

    right_layout.addLayout(view_btn_layout)

    center_splitter = QSplitter(Qt.Horizontal)

    mesh_tab.plotter = QtInteractor(right_container)
    mesh_tab.plotter.set_background("white")
    center_splitter.addWidget(mesh_tab.plotter)

    mesh_tab.inspector_panel = QWidget()
    inspector_layout = QVBoxLayout(mesh_tab.inspector_panel)
    inspector_layout.setContentsMargins(5, 5, 5, 5)

    mesh_tab.pos_label = QLabel("Index: [0, 0, 0]")
    mesh_tab.pos_label.setStyleSheet("font-size: 15px; color: #222222;")
    inspector_layout.addWidget(mesh_tab.pos_label)

    grid_buttons = QGridLayout()
    btn_style = (
        "padding: 6px; font-size: 12px; "
        "color: #111111; background-color: #EFEFEF; "
        "border: 1px solid #CCCCCC; border-radius: 3px;"
    )
    nav_configs = [
        ("Radial Plus", 1, 0, 0, 0, 0), ("Radial Minus", -1, 0, 0, 0, 1),
        ("Theta Plus", 0, 1, 0, 1, 0), ("Theta Minus", 0, -1, 0, 1, 1),
        ("Axial Plus", 0, 0, 1, 2, 0), ("Axial Minus", 0, 0, -1, 2, 1)
    ]
    for txt, di, dj, dk, r, c in nav_configs:
        btn = QPushButton(txt)
        btn.setStyleSheet(btn_style)
        btn.clicked.connect(lambda ch, d=(di, dj, dk): move_inspector_idx(*d))
        grid_buttons.addWidget(btn, r, c)
    inspector_layout.addLayout(grid_buttons)

    inspector_title = QLabel("Element Attributes:")
    inspector_title.setStyleSheet("font-size: 13px; margin-top: 5px; color: #333333;")
    inspector_layout.addWidget(inspector_title)

    mesh_tab.debug_info_box = QTextEdit()
    mesh_tab.debug_info_box.setReadOnly(True)
    mesh_tab.debug_info_box.setStyleSheet("""
        background-color: #1E1E1E; 
        font-family: 'Consolas', 'Courier New', monospace; 
        font-size: 12px; 
        color: #E0E0E0;
        border: 1px solid #444444;
        border-radius: 4px;
        padding: 5px;
    """)
    inspector_layout.addWidget(mesh_tab.debug_info_box)

    mesh_tab.inspector_panel.setVisible(False)

    center_splitter.addWidget(mesh_tab.inspector_panel)
    center_splitter.setStretchFactor(0, 3)
    center_splitter.setStretchFactor(1, 1)

    right_layout.addWidget(center_splitter)

    content_splitter.addWidget(left_container)
    content_splitter.addWidget(right_container)
    content_splitter.setStretchFactor(0, 1) 
    content_splitter.setStretchFactor(1, 3)
    
    main_layout.addWidget(content_splitter, 1)

    status_container = QFrame()
    status_container.setFixedHeight(30)
    status_layout = QHBoxLayout(status_container)
    status_layout.setContentsMargins(10, 0, 10, 0)

    mesh_tab.status_label = QLabel("Status: Ready")
    status_layout.addWidget(mesh_tab.status_label)
    status_layout.addStretch()

    main_layout.addWidget(status_container, 0)
    
    QTimer.singleShot(500, handle_refresh)

    return None