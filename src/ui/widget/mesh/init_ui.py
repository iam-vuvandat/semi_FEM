import sys
import os
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QLabel, QScrollArea, QGroupBox, QApplication)
from PyQt5.QtCore import Qt, QTimer
from pyvistaqt import QtInteractor

# Import bind_input từ project của bạn
try:
    from src.ui.widget.widget.utils.bind_input import bind_input
except ImportError:
    # Hàm dự phòng nếu không tìm thấy module
    def bind_input(obj, attr, factor, callback): return QWidget()

# --- 1. HELPER FUNCTIONS ---
def create_classic_group(title):
    group = QGroupBox(title)
    layout = QFormLayout(group)
    layout.setVerticalSpacing(12) 
    layout.setHorizontalSpacing(25)
    layout.setContentsMargins(15, 20, 15, 15)
    group.setStyleSheet("""
        QGroupBox { 
            font-weight: bold; 
            color: #333;
            border: 1px solid #ccd1d1; 
            border-radius: 4px;
            margin-top: 15px; 
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
        }
    """)
    return group

# --- 2. MAIN UI INITIALIZATION ---
def init_ui(mesh_tab=None):
    if mesh_tab is None: return None

    motor = mesh_tab.main_window.motor
    mesh_data = motor.adaptive_mesh_data 
    
    main_layout = QHBoxLayout(mesh_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    splitter = QSplitter(Qt.Horizontal)

    # --- INTERNAL LOGIC FUNCTIONS ---

    def on_refresh_clicked():
        """Vẽ lại lưới Mesh lên PyVista Plotter"""
        try:
            if mesh_tab is None: return
            cur_motor = mesh_tab.main_window.motor
            
            # Kiểm tra đối tượng mesh tồn tại trong motor
            if hasattr(cur_motor, 'mesh') and cur_motor.mesh is not None:
                mesh_tab.plotter.clear()
                
                # GỌI METHOD show() TỪ CLASS CylindricalMesh CỦA BẠN
                # Không truyền edge_color vì class của bạn đã fix cứng nó rồi
                cur_motor.mesh.show(
                    plotter=mesh_tab.plotter,
                    show_edges=True,
                    opacity=0.3
                )
                
                # Thiết lập góc nhìn chuẩn cho kỹ sư thiết kế máy điện
                mesh_tab.plotter.view_xy()
                mesh_tab.plotter.reset_camera()
                mesh_tab.plotter.render()
        except Exception as e:
            print(f"Lỗi hiển thị Mesh: {e}")

    def on_input_changed():
        """
        CALLBACK QUAN TRỌNG: Được gọi mỗi khi dữ liệu nhập liệu thay đổi.
        Hàm này chứa motor.reload() để làm mới dữ liệu Mesh.
        """
        cur_motor = mesh_tab.main_window.motor
        
        # 1. Gọi reload của motor chính để tính toán lại tọa độ lưới
        if hasattr(cur_motor, 'reload'):
            cur_motor.reload()
            
        # 2. Sau khi motor reload xong, vẽ lại lưới lên giao diện
        on_refresh_clicked()

    # --- UI LAYOUT CONSTRUCTION (LEFT PANEL: INPUTS) ---
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    left_layout.setContentsMargins(0, 0, 10, 0)
    left_layout.setSpacing(12)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    
    config_widget = QWidget()
    config_layout = QVBoxLayout(config_widget)
    config_layout.setSpacing(15)

    groups = {
        "logic":   create_classic_group("Mesh Logic Flags"),
        "r_div":   create_classic_group("Radial Nodes"),
        "t_div":   create_classic_group("Tangential Nodes"),
        "z_div":   create_classic_group("Axial Nodes"),
        "others":  create_classic_group("Other Parameters")
    }
    layouts = {key: gb.layout() for key, gb in groups.items()}

    # Tự động bind các thuộc tính và TRUYỀN CALLBACK vào
    for attr_name, value in vars(mesh_data).items():
        if attr_name.startswith('_'): continue
        display_name = attr_name.replace('n_', '').replace('_', ' ').title()
        
        unit_factor = 1 if attr_name.startswith('n_') else (1e3 if any(k in attr_name.lower() for k in ['dia', 'gap', 'length', 'width', 'opening', 'radius', 'ext']) else 1)
        
        if not attr_name.startswith('n_'):
            if 'arc' in attr_name.lower() or 'angle' in attr_name.lower(): display_name += " (Deg)"
            elif unit_factor == 1e3: display_name += " (mm)"
        
        # CHÈN CALLBACK VÀO ĐÂY: Mỗi khi nhập xong, on_input_changed sẽ chạy
        input_widget = bind_input(
            motor=mesh_data, 
            attr_name=attr_name, 
            unit_factor=unit_factor, 
            callback=on_input_changed
        )
        input_widget.setMinimumHeight(25)

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
        if layouts[key].rowCount() > 0: config_layout.addWidget(groups[key])
    
    config_layout.addStretch()
    scroll.setWidget(config_widget)
    left_layout.addWidget(scroll)

    # LƯU Ý: Nút bấm và ProgressBar đã được loại bỏ theo yêu cầu

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
    
    # Refresh lần đầu khi mở tab
    QTimer.singleShot(1000, on_refresh_clicked)

    return None