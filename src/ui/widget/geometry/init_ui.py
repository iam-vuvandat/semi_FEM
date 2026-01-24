import src.ui.widget.geometry.paths as paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QComboBox, QLabel, QScrollArea, QGroupBox, 
                             QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt
from pyvistaqt import QtInteractor
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(geometry_tab=None):
    if geometry_tab is None: return None

    # 1. TRUY XUẤT DỮ LIỆU TỪ CONTAINER
    motor = geometry_tab.main_window.motor
    stator_params = motor.geometry_data.stator
    rotor_params  = motor.geometry_data.rotor
    
    main_layout = QHBoxLayout(geometry_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    # Splitter thiết lập tỉ lệ 1:1 theo yêu cầu
    splitter = QSplitter(Qt.Horizontal)

    # --- PHẦN BÊN TRÁI: NHẬP LIỆU (Ratio 1) ---
    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 5, 0)

    # Khởi tạo vùng vẽ 3D Interactor
    geometry_tab.plotter = QtInteractor(geometry_tab)
    geometry_tab.plotter.set_background("white")

    # 2. HÀM CẬP NHẬT TOÀN CỤC (CENTRAL RELOAD LOGIC)
    def global_update():
        """
        Thực hiện reload toàn bộ hệ thống (Matrix, CAD, Mesh) 
        trước khi cập nhật hiển thị.
        """
        if motor is None: return
        
        # Gọi hàm reload trung tâm của đối tượng motor
        motor.reload() 
        
        # Làm sạch và vẽ lại mô hình CAD mới nhất
        try:
            geometry_tab.plotter.disable_picking()
        except:
            pass
            
        geometry_tab.plotter.clear()
        if motor.geometry is not None:
            # Hiển thị Geometry đã được tạo mới trong motor.reload()
            motor.geometry.show(plotter=geometry_tab.plotter, show_axes=True)
            geometry_tab.plotter.view_isometric()
            geometry_tab.plotter.reset_camera()
            geometry_tab.plotter.update()
        
        print(f"[UI] Motor Reloaded & 3D Updated. Symmetry: {motor.symmetry_factor}")

    # Motor Type Selector
    type_layout = QFormLayout()
    geometry_tab.motor_type_combo = QComboBox()
    geometry_tab.motor_type_combo.addItems(["Axial Flux Motor Type 1", "SPMSM", "IPM"])
    type_layout.addRow("<b>Motor Type:</b>", geometry_tab.motor_type_combo)
    left_layout.addLayout(type_layout)

    # Scroll Area chứa các cột thông số
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    
    content_widget = QWidget()
    # Layout 2 cột cho Stator và Rotor
    content_hbox = QHBoxLayout(content_widget)
    content_hbox.setSpacing(10)
    content_hbox.setAlignment(Qt.AlignTop)

    # 3. HÀM QUÉT THUỘC TÍNH ĐỘNG (DYNAMIC SCANNING)
    def create_dynamic_group(title, container):
        group = QGroupBox(title)
        # Sử dụng Stylesheet để in đậm thay vì HTML tag
        group.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #dee2e6; margin-top: 10px; }")
        layout = QFormLayout(group)
        
        for key in vars(container):
            if key.startswith('_'): continue
            
            # ĐỊNH DẠNG NHÃN: Viết hoa chữ cái đầu, thay '_' bằng dấu cách
            display_label = key.replace('_', ' ').title()
            
            # Tự động xác định hệ số đơn vị dựa trên tên thuộc tính
            dim_keywords = ['dia', 'length', 'depth', 'width', 'opening', 'gap', 'radius', 'ext']
            unit = 1e3 if any(k in key.lower() for k in dim_keywords) else 1
            
            # Kết nối bind_input với hàm global_update
            input_widget = bind_input(container, key, unit, global_update)
            layout.addRow(f"{display_label}:", input_widget)
            
        return group

    # Thêm 2 cột thông số vào Scroll Area
    content_hbox.addWidget(create_dynamic_group("Stator Parameters", stator_params))
    content_hbox.addWidget(create_dynamic_group("Rotor Parameters", rotor_params))
    
    scroll.setWidget(content_widget)
    left_layout.addWidget(scroll)

    # --- PHẦN BÊN PHẢI: RENDER 3D (Ratio 1) ---
    right_panel = QFrame()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)
    
    # Gắn PyVista Plotter vào phần bên phải
    right_layout.addWidget(geometry_tab.plotter)

    # Nút bấm thủ công
    btn_reload = QPushButton("Force Full System Reload")
    btn_reload.setFixedHeight(35)
    btn_reload.clicked.connect(global_update)
    right_layout.addWidget(btn_reload)

    # 4. THIẾT LẬP TỈ LỆ CHIA ĐÔI 1:1
    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setStretchFactor(0, 1) # Left
    splitter.setStretchFactor(1, 1) # Right
    
    main_layout.addWidget(splitter)
    
    # Khởi tạo mô hình lần đầu ngay khi mở Tab
    global_update()
    
    return None