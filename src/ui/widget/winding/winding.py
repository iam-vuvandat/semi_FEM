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

    def refresh(self):
        """
        Kiểm tra trạng thái lỗi thời và cập nhật lại tab Winding.
        Được gọi tự động khi người dùng click vào Tab này.
        """
        motor = self.main_window.motor
        if motor:
            # 1. Kiểm tra trạng thái: Nếu bạn vừa sửa số rãnh ở Tab Geometry, 
            # lệnh require này sẽ tự động chạy lại logic tính toán dây quấn.
            motor.require("winding_data")
            
            # 2. Cập nhật nội dung hiển thị (Ma trận, Đồ thị)
            # Hàm 'refresh_content' này thường được gán bên trong file init_ui.py
            if hasattr(self, 'refresh_content'):
                self.refresh_content()
            
            # Giữ lại logic cũ của bạn nếu cần cập nhật bảng cụ thể
            elif hasattr(self, 'matrix_table') and self.matrix_table:
                from src.ui.widget.winding.init_ui import update_winding_table
                update_winding_table(self, motor)