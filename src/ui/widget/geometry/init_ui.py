import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QScrollArea, QGroupBox, QApplication)
from PyQt5.QtCore import Qt, QTimer
from pyvistaqt import QtInteractor
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(geometry_tab=None):
    if geometry_tab is None: 
        return None

    main_win = geometry_tab.main_window
    motor = main_win.motor
    stator_params = motor.geometry_data.stator
    rotor_params = motor.geometry_data.rotor
    
    main_layout = QHBoxLayout(geometry_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    splitter = QSplitter(Qt.Horizontal)

    geometry_tab.plotter = QtInteractor(geometry_tab)
    geometry_tab.plotter.set_background("white")

    def refresh_plot():
        geometry_tab.plotter.clear()
        if motor.geometry is not None:
            motor.geometry.show(plotter=geometry_tab.plotter, show_axes=True)
            geometry_tab.plotter.view_isometric()
            geometry_tab.plotter.reset_camera()
            geometry_tab.plotter.render()

    def handle_refresh():
        if motor is None:
            return
        if (motor.motor_state_manager.ready_state.winding_data and 
            motor.motor_state_manager.ready_state.geometry):
            return 
        motor.require("geometry")
        refresh_plot()
        QApplication.processEvents()

    def on_input_changed():
        motor.just_changed("geometry")
        handle_refresh()

    geometry_tab.refresh = handle_refresh
    geometry_tab.refresh_plot = refresh_plot

    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 0, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    
    content_widget = QWidget()
    content_layout = QHBoxLayout(content_widget)
    content_layout.setSpacing(10)
    content_layout.setAlignment(Qt.AlignTop)

    def create_dynamic_group(title, container):
        group = QGroupBox(title)
        layout = QFormLayout(group)
        layout.setVerticalSpacing(8)
        
        for key in vars(container):
            if key.startswith('_'):
                continue
            
            display_label = key.replace('_', ' ').title()
            dim_keywords = ['dia', 'length', 'depth', 'width', 'opening', 'gap', 'radius', 'ext', 'embed']
            is_dimension = any(k in key.lower() for k in dim_keywords)
            unit = 1000.0 if is_dimension else 1.0
            
            if 'arc' in key.lower() or 'angle' in key.lower():
                display_label += " (°)"
            elif is_dimension:
                display_label += " (mm)"
            
            input_widget = bind_input(
                motor=container, 
                attr_name=key, 
                unit_factor=unit, 
                callback=on_input_changed
            )
            input_widget.setFixedWidth(70) 
            layout.addRow(f"{display_label}:", input_widget)
            
        return group

    content_layout.addWidget(create_dynamic_group("Stator Geometry", stator_params))
    content_layout.addWidget(create_dynamic_group("Rotor Geometry", rotor_params))
    content_layout.addStretch()

    scroll.setWidget(content_widget)
    left_layout.addWidget(scroll)

    right_panel = QFrame()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.addWidget(geometry_tab.plotter)

    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    
    splitter.setSizes([500, 500])
    splitter.setStretchFactor(0, 1) 
    splitter.setStretchFactor(1, 1) 
    
    main_layout.addWidget(splitter)
    
    QTimer.singleShot(100, handle_refresh)
    
    return None