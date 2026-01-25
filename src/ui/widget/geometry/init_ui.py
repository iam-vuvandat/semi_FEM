import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QComboBox, QLabel, QScrollArea, QGroupBox, 
                             QPushButton, QApplication, QTabWidget)
from PyQt5.QtCore import Qt, QTimer
from pyvistaqt import QtInteractor
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(geometry_tab=None):
    if geometry_tab is None: 
        return None

    # Lấy tham chiếu đến MainWindow và đối tượng Widget (QTabWidget)
    main_win = geometry_tab.main_window
    motor = main_win.motor
    stator_params = motor.geometry_data.stator
    rotor_params  = motor.geometry_data.rotor
    
    # Đối tượng Widget (QTabWidget) chứa tất cả các Tab
    # Dựa trên class Widget(QTabWidget) bạn cung cấp
    parent_widget = geometry_tab.parentWidget()
    if not isinstance(parent_widget, QTabWidget):
        # Phòng trường hợp cấu trúc phân cấp widget sâu hơn
        parent_widget = main_win.findChild(QTabWidget)

    # Thiết lập Layout chính cho Tab Geometry
    main_layout = QHBoxLayout(geometry_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    splitter = QSplitter(Qt.Horizontal)

    # Khởi tạo Plotter hiển thị hình học 3D
    geometry_tab.plotter = QtInteractor(geometry_tab)
    geometry_tab.plotter.set_background("white")

    # --- HÀM CẬP NHẬT TOÀN HỆ THỐNG (TÁI TẠO TAB) ---
    def global_update():
        if motor is None: 
            return
        
        # 1. Thực hiện Reload logic lõi (Tính toán lại máy điện)
        motor.reload() 
        
        # 2. Cập nhật hiển thị tại Tab hiện tại (Geometry)
        geometry_tab.plotter.clear()
        if motor.geometry is not None:
            motor.geometry.show(plotter=geometry_tab.plotter, show_axes=True)
            geometry_tab.plotter.view_isometric()
            geometry_tab.plotter.reset_camera()
            geometry_tab.plotter.render()

        # 3. TÁI TẠO TAB WINDING & MESH (Sử dụng các method bạn cung cấp)
        # Chúng ta sẽ xóa tab cũ và gọi setup_..._widget để tạo mới hoàn toàn
        if parent_widget and hasattr(parent_widget, 'setup_winding_widget'):
            try:
                # --- Xử lý Tab Winding ---
                if hasattr(parent_widget, 'winding_tab'):
                    idx_w = parent_widget.indexOf(parent_widget.winding_tab)
                    if idx_w != -1:
                        # Lưu tiêu đề cũ
                        title_w = parent_widget.tabText(idx_w)
                        # Xóa tab cũ khỏi QTabWidget
                        parent_widget.removeTab(idx_w)
                        # Hủy instance cũ
                        parent_widget.winding_tab.deleteLater()
                        # Tái tạo bằng method bạn cho phép
                        # Method này sẽ khởi tạo lại UI và nạp dữ liệu motor mới nhất
                        parent_widget.winding_tab = parent_widget.setup_winding_widget()
                        # Đưa tab mới vào đúng vị trí cũ
                        parent_widget.insertTab(idx_w, parent_widget.winding_tab, title_w)

                # --- Xử lý Tab Mesh ---
                if hasattr(parent_widget, 'mesh_tab'):
                    idx_m = parent_widget.indexOf(parent_widget.mesh_tab)
                    if idx_m != -1:
                        title_m = parent_widget.tabText(idx_m)
                        parent_widget.removeTab(idx_m)
                        parent_widget.mesh_tab.deleteLater()
                        # Tái tạo Tab Mesh mới
                        parent_widget.mesh_tab = parent_widget.setup_mesh_widget()
                        parent_widget.insertTab(idx_m, parent_widget.mesh_tab, title_m)
                
                print("DEBUG: Đã tái tạo thành công Tab Winding và Tab Mesh.")
            
            except Exception as e:
                print(f"Lỗi khi thực hiện tái tạo Tab: {e}")

        # Ép giao diện xử lý các sự kiện vẽ ngay lập tức để tránh 'Lazy Update'
        QApplication.processEvents()

    # --- PHẦN XÂY DỰNG GIAO DIỆN NHẬP LIỆU (LEFT PANEL) ---
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
            
            # Logic xác định đơn vị đo lường
            dim_keywords = ['dia', 'length', 'depth', 'width', 'opening', 'gap', 'radius', 'ext', 'embed']
            is_dimension = any(k in key.lower() for k in dim_keywords)
            unit = 1e3 if is_dimension else 1
            
            if 'arc' in key.lower() or 'angle' in key.lower():
                display_label += " (Deg)"
            elif is_dimension:
                display_label += " (mm)"
            
            # Gắn global_update vào callback để mọi thay đổi kích hoạt chuỗi cập nhật
            input_widget = bind_input(container, key, unit, global_update)
            layout.addRow(f"{display_label}:", input_widget)
            
        return group

    # Thêm Stator và Rotor vào giao diện
    content_hbox.addWidget(create_dynamic_group("Stator Geometry", stator_params))
    content_hbox.addWidget(create_dynamic_group("Rotor Geometry", rotor_params))
    
    scroll.setWidget(content_widget)
    left_layout.addWidget(scroll)

    # --- PHẦN HIỂN THỊ ĐỒ HỌA 3D (RIGHT PANEL) ---
    right_panel = QFrame()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(0, 0, 0, 0)
    right_layout.addWidget(geometry_tab.plotter)

    # Nút bấm cưỡng bức cập nhật trong trường hợp cần thiết
    btn_reload = QPushButton("Force Recreate System")
    btn_reload.setFixedHeight(40)
    btn_reload.setStyleSheet("""
        QPushButton { 
            font-weight: bold; 
            background-color: #f0f7fb; 
            border: 1px solid #c5ddec;
            border-radius: 4px;
        }
        QPushButton:hover { background-color: #e1f0f7; }
    """)
    btn_reload.clicked.connect(global_update)
    right_layout.addWidget(btn_reload)

    # Cấu hình Splitter
    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    splitter.setStretchFactor(0, 1) 
    splitter.setStretchFactor(1, 1) 
    
    main_layout.addWidget(splitter)
    
    # Tự động thực hiện cập nhật lần đầu tiên khi mở Tab
    QTimer.singleShot(500, global_update)
    
    return None