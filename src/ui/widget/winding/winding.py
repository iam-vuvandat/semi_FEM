import paths
from PyQt5.QtWidgets import QWidget
from src.ui.widget.winding.init_ui import init_ui

class Winding(QWidget):
    def __init__(self, parent_widget):
        """
        Khởi tạo tab Dây quấn tổng quát.
        Sử dụng chung cho tất cả các loại động cơ (Axial Flux, SPMSM, IPM, SynRM).
        """
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        
        # Luôn lấy motor từ MainWindow để đảm bảo dữ liệu đồng bộ
        self.main_window = self.parent_widget.main_window
        
        # Các tham chiếu UI sẽ được khởi tạo trong init_ui
        self.type_combo = None
        self.matrix_table = None
        
        # Khởi tạo giao diện
        self.init_ui()

    def init_ui(self):
        return init_ui(winding_tab=self)

    def refresh_tab(self):
        """
        Cập nhật lại bảng ma trận dây quấn khi có thay đổi từ tab Geometry 
        (ví dụ: đổi Slot Number hoặc Pole Number).
        """
        if hasattr(self, 'matrix_table') and self.matrix_table:
            from src.ui.widget.winding.init_ui import update_winding_table
            # Cập nhật lại dữ liệu từ motor vào giao diện bảng
            update_winding_table(self, self.main_window.motor)