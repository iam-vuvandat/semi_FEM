import paths
from PyQt5.QtWidgets import QWidget
from src.ui.widget.input_data.init_ui import init_ui

class InputData(QWidget):
    def __init__(self, parent_widget):
        """
        Khởi tạo tab Input Data.
        Nơi gán vật liệu và thiết lập các thông số vật lý cho từng Part của động cơ.
        """
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        
        # Truy cập motor thông qua MainWindow để đảm bảo dữ liệu nhất quán
        self.main_window = self.parent_widget.main_window
        
        # Các thuộc tính UI (như Table hay Canvas đồ thị) sẽ được khởi tạo trong init_ui
        self.material_table = None
        self.canvas = None # Placeholder cho đồ thị Matplotlib sau này
        
        # Thiết lập giao diện
        self.init_ui()

    def init_ui(self):
        """Xây dựng giao diện cho tab Input Data"""
        return init_ui(input_tab=self)

    def refresh_tab(self):
        """
        Làm mới bảng vật liệu khi Geometry thay đổi 
        (ví dụ: khi thêm rãnh stator hoặc thay đổi số lượng nam châm).
        """
        if hasattr(self, 'material_table') and self.material_table:
            from src.ui.widget.input_data.init_ui import refresh_material_table
            refresh_material_table(self, self.main_window.motor)