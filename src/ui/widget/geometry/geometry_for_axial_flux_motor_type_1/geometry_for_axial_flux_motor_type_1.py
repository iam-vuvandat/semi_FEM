from re import A
import paths
from PyQt5.QtWidgets import QWidget
from src.ui.widget.geometry.geometry_for_axial_flux_motor_type_1.init_ui import init_ui
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1

class GeometryForAxialFluxType1(QWidget):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.main_window = self.parent_widget.main_window
        if self.main_window.motor is None:
            self.main_window.motor = AxialFluxMotorType1()
        
        # Các thuộc tính UI cần quản lý
        self.motor_type_combo = None
        self.plotter = None
        
        # Gọi hàm khởi tạo UI từ file riêng
        self.init_ui()

    def init_ui(self):
        return init_ui(geometry_tab=self)