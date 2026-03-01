import paths
from PyQt5.QtWidgets import QWidget
from src.ui.widget.geometry.init_ui import init_ui

class Geometry(QWidget):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.main_window = self.parent_widget.main_window
        
        # Các thuộc tính UI cần quản lý
        self.motor_type_combo = None
        self.plotter = None
        
        # Gọi hàm khởi tạo UI từ file riêng
        self.init_ui()

    def init_ui(self):
        return init_ui(geometry_tab=self)

    def refresh(self):
        """Kiểm tra trạng thái lỗi thời của property, nếu lỗi thời mới thực hiện nạp lại."""
        motor = self.main_window.motor
        if motor:
            # 1. require() sẽ tự kiểm tra ready_state.geometry
            # Nếu đã True (không sửa gì) -> nó thoát ngay lập tức, cực nhanh.
            # Nếu False (vừa sửa input) -> nó tự nạp Winding -> Geometry.
            motor.require("geometry")
            
            # 2. Gọi hàm vẽ lại 3D (hàm này được gán bên trong init_ui)
            if hasattr(self, "refresh_plot"):
                self.refresh_plot()