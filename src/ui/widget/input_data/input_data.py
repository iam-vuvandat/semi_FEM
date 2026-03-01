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

    def refresh(self):
        """
        Hàm refresh thông minh: 
        Kiểm tra trạng thái lỗi thời của Material Database trước khi hiển thị.
        """
        motor = self.main_window.motor
        if motor:
            # 1. Kiểm tra trạng thái: Nếu dữ liệu vật liệu đã bị đánh dấu 'thối' (False),
            # require sẽ tự động chạy lại motor.create_material_database().
            motor.require("material_database")
            
            # 2. Cập nhật nội dung hiển thị (Bảng vật liệu hoặc tóm tắt thông số)
            # Ưu tiên gọi hàm refresh_content được gán trong init_ui
            if hasattr(self, 'refresh_content'):
                self.refresh_content()
            
            # Giữ lại logic cũ của bạn để đảm bảo tính tương thích
            elif hasattr(self, 'material_table') and self.material_table:
                from src.ui.widget.input_data.init_ui import refresh_material_table
                refresh_material_table(self, motor)