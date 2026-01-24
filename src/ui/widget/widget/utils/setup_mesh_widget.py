import paths
from src.ui.widget.mesh.mesh import Mesh

def setup_mesh_widget(widget):
    """
    Hàm khởi tạo hoặc làm mới Tab Mesh.
    """
    # 1. Xác định motor_type để linh hoạt mở rộng sau này
    if widget.main_window.motor is not None:
        motor_type = widget.main_window.motor.motor_type
    else:
        # Mặc định nếu motor chưa khởi tạo (tránh crash app khi mở)
        motor_type = "axial_flux_motor_type_1"

    # 2. KIỂM SOÁT BỘ NHỚ: Nếu tab Mesh đã tồn tại, xóa bỏ hoàn toàn
    # Giả sử Mesh là tab thứ 4 (index 3)
    if widget.mesh_tab is not None:
        # Xóa khỏi QTabWidget
        index = widget.indexOf(widget.mesh_tab)
        if index != -1:
            widget.removeTab(index)
        
        # Giải phóng bộ nhớ RAM cho Surface Pro 5
        widget.mesh_tab.deleteLater()
        widget.mesh_tab = None

    # 3. KHỞI TẠO TAB MỚI
    # (Bạn có thể thêm logic rẽ nhánh if motor_type == ... ở đây)
    widget.mesh_tab = Mesh(parent_widget=widget)
    
    # 4. THÊM TAB VÀO GIAO DIỆN
    widget.addTab(widget.mesh_tab, "Mesh")
    
    return widget.mesh_tab
