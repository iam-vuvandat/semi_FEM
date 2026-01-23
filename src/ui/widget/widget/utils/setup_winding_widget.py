import paths
from src.ui.widget.winding.winding import Winding

def setup_winding_widget(widget):
    """
    Khởi tạo và quản lý tab Winding.
    Duy trì sự đồng bộ với cách quản lý của setup_geometry_widget.
    """
    # 1. Kiểm tra và dọn dẹp tab Winding cũ (nếu có) để tránh rò rỉ bộ nhớ
    if hasattr(widget, 'winding_tab') and widget.winding_tab is not None:
        # Tìm index của tab Winding để xóa chính xác
        index = widget.indexOf(widget.winding_tab)
        if index != -1:
            widget.removeTab(index)
        
        widget.winding_tab.deleteLater()
        widget.winding_tab = None

    # 2. Khởi tạo class Winding (Sử dụng class tổng quát như bạn yêu cầu)
    widget.winding_tab = Winding(parent_widget=widget)

    # 3. Chèn tab vào vị trí thứ 2 (index 1) - Ngay sau tab Geometry
    if widget.winding_tab is not None:
        # Chúng ta chèn vào index 1 để đảm bảo thứ tự: Geometry (0) -> Winding (1)
        widget.insertTab(1, widget.winding_tab, "Winding")
        
    return widget.winding_tab