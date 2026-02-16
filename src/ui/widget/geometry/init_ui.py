import paths
import sys
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QLabel, QScrollArea, QGroupBox, 
                             QPushButton, QApplication, QTabWidget)
from PyQt5.QtCore import Qt, QTimer
from pyvistaqt import QtInteractor
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(geometry_tab=None):
    if geometry_tab is None: 
        return None

    main_win = geometry_tab.main_window
    motor = main_win.motor
    stator_params = motor.geometry_data.stator
    rotor_params  = motor.geometry_data.rotor
    
    parent_widget = geometry_tab.parentWidget()
    if not isinstance(parent_widget, QTabWidget):
        parent_widget = main_win.findChild(QTabWidget)

    main_layout = QHBoxLayout(geometry_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    splitter = QSplitter(Qt.Horizontal)

    geometry_tab.plotter = QtInteractor(geometry_tab)
    geometry_tab.plotter.set_background("white")

    def global_update():
        if motor is None: 
            return
        
        motor.reload() 
        
        geometry_tab.plotter.clear()
        if motor.geometry is not None:
            motor.geometry.show(plotter=geometry_tab.plotter, show_axes=True)
            geometry_tab.plotter.view_isometric()
            geometry_tab.plotter.reset_camera()
            geometry_tab.plotter.render()

        if parent_widget and hasattr(parent_widget, 'setup_winding_widget'):
            try:
                if hasattr(parent_widget, 'winding_tab'):
                    idx_w = parent_widget.indexOf(parent_widget.winding_tab)
                    if idx_w != -1:
                        title_w = parent_widget.tabText(idx_w)
                        parent_widget.removeTab(idx_w)
                        parent_widget.winding_tab.deleteLater()
                        parent_widget.winding_tab = parent_widget.setup_winding_widget()
                        parent_widget.insertTab(idx_w, parent_widget.winding_tab, title_w)

                if hasattr(parent_widget, 'mesh_tab'):
                    idx_m = parent_widget.indexOf(parent_widget.mesh_tab)
                    if idx_m != -1:
                        title_m = parent_widget.tabText(idx_m)
                        parent_widget.removeTab(idx_m)
                        parent_widget.mesh_tab.deleteLater()
                        parent_widget.mesh_tab = parent_widget.setup_mesh_widget()
                        parent_widget.insertTab(idx_m, parent_widget.mesh_tab, title_m)
                
                print("DEBUG: Tab regeneration successful.")
            
            except Exception as e:
                print(f"Error regenerating tabs: {e}")

        QApplication.processEvents()

    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 10, 0)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    
    content_widget = QWidget()
    content_hbox = QHBoxLayout(content_widget)

    def create_dynamic_group(title, container):
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox { 
                font-weight: bold; 
                border: 1px solid #dee2e6; 
                border-radius: 4px;
                margin-top: 15px; 
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout = QFormLayout(group)
        layout.setVerticalSpacing(10)
        
        for key in vars(container):
            if key.startswith('_'): 
                continue
            
            display_label = key.replace('_', ' ').title()
            
            dim_keywords = ['dia', 'length', 'depth', 'width', 'opening', 'gap', 'radius', 'ext', 'embed']
            is_dimension = any(k in key.lower() for k in dim_keywords)
            unit = 1e3 if is_dimension else 1
            
            if 'arc' in key.lower() or 'angle' in key.lower():
                display_label += " (Deg)"
            elif is_dimension:
                display_label += " (mm)"
            
            input_widget = bind_input(container, key, unit, global_update)
            layout.addRow(f"{display_label}:", input_widget)
            
        return group

    content_hbox.addWidget(create_dynamic_group("Stator Geometry", stator_params))
    content_hbox.addWidget(create_dynamic_group("Rotor Geometry", rotor_params))
    
    scroll.setWidget(content_widget)
    left_layout.addWidget(scroll)

    right_panel = QFrame()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)
    
    right_layout.addWidget(geometry_tab.plotter)

    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setStretchFactor(0, 1) 
    splitter.setStretchFactor(1, 1) 
    
    main_layout.addWidget(splitter)
    
    QTimer.singleShot(500, global_update)
    
    return None