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
        
        # Thiết lập giao diện
        self.init_ui()

    def init_ui(self):
        """Xây dựng giao diện cho tab Mesh"""
        return init_ui(mesh_tab=self)

    def refresh_tab(self):
        """
        Làm mới giao diện tab Mesh khi dữ liệu motor thay đổi.
        """
        # Logic này sẽ được gọi để đồng bộ lại dữ liệu lên UI
        from src.ui.widget.mesh.init_ui import refresh_mesh_display
        refresh_mesh_display(self, self.main_window.motor)