import paths
from PyQt5.QtWidgets import QWidget
from src.ui.widget.mesh.init_ui import init_ui

class Mesh(QWidget):
    def __init__(self, parent_widget):
        """
        Khởi tạo tab Mesh.
        Nơi thiết lập các thông số chia lưới (discretization) cho mô hình 3D MBGRN.
        """
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        
        # Truy cập motor thông qua MainWindow để đảm bảo dữ liệu nhất quán
        self.main_window = self.parent_widget.main_window
        
        # Các thuộc tính UI sẽ được khởi tạo trong init_ui tùy theo thiết kế của bạn
        self.plotter = None
        
        # Thiết lập giao diện
        self.init_ui()

    def init_ui(self):
        """Xây dựng giao diện cho tab Mesh"""
        return init_ui(mesh_tab=self)

    def refresh(self):
        """
        Hàm refresh thông minh: 
        Chỉ thực hiện chia lưới lại nếu thông số Hình học hoặc Mesh Nodes bị thay đổi.
        """
        motor = self.main_window.motor
        if motor:
            # 1. Kiểm tra trạng thái: Nếu cờ 'ready_state.mesh' là False,
            # require sẽ tự động chạy chuỗi Winding -> Geometry -> Mesh.
            motor.require("mesh")
            
            # 2. Cập nhật hiển thị 3D Mesh
            # Ưu tiên gọi hàm refresh_content được gán trong init_ui
            if hasattr(self, 'refresh_content'):
                self.refresh_content()
            
            # Giữ lại logic cũ của bạn để đảm bảo tương thích với file init_ui gốc
            elif hasattr(self, 'plotter'):
                from src.ui.widget.mesh.init_ui import refresh_mesh_display
                refresh_mesh_display(self, motor)