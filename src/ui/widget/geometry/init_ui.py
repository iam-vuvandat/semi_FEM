import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QComboBox, QLabel, QScrollArea, QGroupBox, 
                             QPushButton)
from PyQt5.QtCore import Qt
from pyvistaqt import QtInteractor
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(geometry_tab=None):
    if geometry_tab is None: return None

    motor = geometry_tab.main_window.motor
    stator_params = motor.geometry_data.stator
    rotor_params  = motor.geometry_data.rotor
    
    main_layout = QHBoxLayout(geometry_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    splitter = QSplitter(Qt.Horizontal)

    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)

    geometry_tab.plotter = QtInteractor(geometry_tab)
    geometry_tab.plotter.set_background("white")

    def global_update():
        if motor is None: return
        motor.reload() 
        
        geometry_tab.plotter.clear()
        if motor.geometry is not None:
            motor.geometry.show(plotter=geometry_tab.plotter, show_axes=True)
            geometry_tab.plotter.view_isometric()
            geometry_tab.plotter.reset_camera()
            geometry_tab.plotter.update()
        

    # Scroll Area chứa thông số hình học
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    
    content_widget = QWidget()
    content_hbox = QHBoxLayout(content_widget)

    def create_dynamic_group(title, container):
        group = QGroupBox(title)
        group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #dee2e6; margin-top: 10px; }")
        layout = QFormLayout(group)
        
        for key in vars(container):
            if key.startswith('_'): continue
            
            display_label = key.replace('_', ' ').title()
            
            # Kiểm tra từ khóa đơn vị
            dim_keywords = ['dia', 'length', 'depth', 'width', 'opening', 'gap', 'radius', 'ext', 'embed']
            is_dimension = any(k in key.lower() for k in dim_keywords)
            unit = 1e3 if is_dimension else 1
            
            # --- CẬP NHẬT LOGIC NHÃN ĐƠN VỊ ---
            if 'arc' in key.lower() or 'angle' in key.lower():
                display_label += " (Deg)"
            elif is_dimension:
                display_label += " (mm)"
            
            # Gọi bind_input theo đúng cấu trúc tham số vị trí của bạn
            input_widget = bind_input(container, key, unit, global_update)
            layout.addRow(f"{display_label}:", input_widget)
            
        return group

    content_hbox.addWidget(create_dynamic_group("Stator Parameters", stator_params))
    content_hbox.addWidget(create_dynamic_group("Rotor Parameters", rotor_params))
    
    scroll.setWidget(content_widget)
    left_layout.addWidget(scroll)

    # Render 3D và nút điều khiển
    right_panel = QFrame()
    right_layout = QVBoxLayout(right_panel)
    right_layout.addWidget(geometry_tab.plotter)

    btn_reload = QPushButton("Force Full System Reload")
    btn_reload.setFixedHeight(35)
    btn_reload.clicked.connect(global_update)
    right_layout.addWidget(btn_reload)

    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setStretchFactor(0, 1) 
    splitter.setStretchFactor(1, 1) 
    
    main_layout.addWidget(splitter)
    global_update()
    
    return None