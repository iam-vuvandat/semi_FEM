import paths

from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QComboBox, QLabel, QGridLayout, QScrollArea)
from PyQt5.QtCore import Qt
from pyvistaqt import QtInteractor
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(geometry_tab=None):
    if geometry_tab is None: return None

    motor = geometry_tab.main_window.motor
    if motor is None:
        print("[ERROR] Motor object is None in init_ui!")
        return None

    main_layout = QHBoxLayout(geometry_tab)
    splitter = QSplitter(Qt.Horizontal)
    
    # --- PHẦN BÊN TRÁI: NHẬP LIỆU (Giữ nguyên ScrollArea của bạn) ---
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setFrameShape(QFrame.NoFrame)
    container = QWidget()
    v_layout = QVBoxLayout(container)
    
    # Motor Type Layout
    t_layout = QFormLayout()
    geometry_tab.motor_type_combo = QComboBox()
    geometry_tab.motor_type_combo.addItems(["Axial Flux Motor Type 1", "SPMSM", "IPM"])
    t_layout.addRow("<b>Motor type:</b>", geometry_tab.motor_type_combo)
    v_layout.addLayout(t_layout)

    # Khởi tạo vùng vẽ 3D Render
    geometry_tab.plotter = QtInteractor(geometry_tab)
    geometry_tab.plotter.set_background("white")

    def render_3d():
        if motor is None: return
        
        # SỬA LỖI: Tắt picking cũ trước khi vẽ lại để tránh crash PyVista
        try:
            geometry_tab.plotter.disable_picking()
        except: pass
        
        geometry_tab.plotter.clear()
        if motor.geometry is None:
            motor.create_geometry()
        
        if motor.geometry is not None:
            motor.geometry.show(plotter=geometry_tab.plotter, show_axes=True)
            geometry_tab.plotter.view_isometric()
            geometry_tab.plotter.reset_camera()
            geometry_tab.plotter.update()

    # --- GRID TOÀN BỘ 24 THAM SỐ (Giữ nguyên bố cục của bạn) ---
    grid = QGridLayout()
    style = "background-color: #e9ecef; border-radius: 3px; font-weight: bold; padding: 2px;"
    
    grid.addWidget(QLabel("<b>Stator parameter</b>"), 0, 0, Qt.AlignCenter)
    grid.addWidget(QLabel("<b>Rotor parameter</b>"), 0, 1, Qt.AlignCenter)

    # --- SECTION: RADIAL ---
    l_r = QLabel("Radial Parameters"); l_r.setStyleSheet(style)
    grid.addWidget(l_r, 1, 0, 1, 2, Qt.AlignCenter)

    # Radial - Stator (6 fields)
    f_s_r = QFormLayout()
    f_s_r.addRow("Slot Number:", bind_input(motor, "slot_number", 1, render_3d))
    f_s_r.addRow("Lam Dia (mm):", bind_input(motor, "stator_lam_dia", 1e3, render_3d))
    f_s_r.addRow("Bore Dia (mm):", bind_input(motor, "stator_bore_dia", 1e3, render_3d))
    f_s_r.addRow("Slot Opening (mm):", bind_input(motor, "slot_opening", 1e3, render_3d))
    f_s_r.addRow("Wdg Ext In (mm):", bind_input(motor, "wdg_extension_inner", 1e3, render_3d))
    f_s_r.addRow("Wdg Ext Out (mm):", bind_input(motor, "wdg_extension_outer", 1e3, render_3d))
    grid.addLayout(f_s_r, 2, 0)

    # Radial - Rotor (9 fields)
    f_r_r = QFormLayout()
    f_r_r.addRow("Pole Number:", bind_input(motor, "pole_number", 1, render_3d))
    f_r_r.addRow("Lam Dia (mm):", bind_input(motor, "rotor_lam_dia", 1e3, render_3d))
    f_r_r.addRow("Mag Arc (deg):", bind_input(motor, "magnet_arc", 1, render_3d))
    f_r_r.addRow("Mag Embed (mm):", bind_input(motor, "magnet_embed_depth", 1e3, render_3d))
    f_r_r.addRow("Mag Depth (mm):", bind_input(motor, "magnet_depth", 1e3, render_3d))
    f_r_r.addRow("Mag Segments:", bind_input(motor, "magnet_segments", 1, render_3d))
    f_r_r.addRow("Banding (mm):", bind_input(motor, "banding_depth", 1e3, render_3d))
    f_r_r.addRow("Shaft Dia (mm):", bind_input(motor, "shaft_dia", 1e3, render_3d))
    f_r_r.addRow("Shaft Hole (mm):", bind_input(motor, "shaft_hole_diameter", 1e3, render_3d))
    grid.addLayout(f_r_r, 2, 1)

    # --- SECTION: AXIAL ---
    l_a = QLabel("Axial Parameters"); l_a.setStyleSheet(style)
    grid.addWidget(l_a, 3, 0, 1, 2, Qt.AlignCenter)

    # Axial - Stator (6 fields)
    f_s_a = QFormLayout()
    f_s_a.addRow("Stator Len (mm):", bind_input(motor, "stator_length", 1e3, render_3d))
    f_s_a.addRow("Slot Width (mm):", bind_input(motor, "slot_width", 1e3, render_3d))
    f_s_a.addRow("Slot Depth (mm):", bind_input(motor, "slot_depth", 1e3, render_3d))
    f_s_a.addRow("Corner Rad (deg):", bind_input(motor, "slot_corner_radius", 1, render_3d))
    f_s_a.addRow("Tip Depth (mm):", bind_input(motor, "tooth_tip_depth", 1e3, render_3d))
    f_s_a.addRow("Tip Angle (deg):", bind_input(motor, "tooth_tip_angle", 1, render_3d))
    grid.addLayout(f_s_a, 4, 0)

    # Axial - Rotor (3 fields)
    f_r_a = QFormLayout()
    f_r_a.addRow("Airgap (mm):", bind_input(motor, "airgap", 1e3, render_3d))
    f_r_a.addRow("Mag Length (mm):", bind_input(motor, "magnet_length", 1e3, render_3d))
    f_r_a.addRow("Rotor Length (mm):", bind_input(motor, "rotor_length", 1e3, render_3d))
    grid.addLayout(f_r_a, 4, 1)

    v_layout.addLayout(grid)
    v_layout.addStretch()
    scroll_area.setWidget(container)

    # --- KẾT NỐI SPLITTER ---
    splitter.addWidget(scroll_area)
    splitter.addWidget(geometry_tab.plotter)
    splitter.setStretchFactor(1, 2)
    main_layout.addWidget(splitter)

    render_3d()
    return None