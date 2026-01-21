import paths
from PyQt5.QtWidgets import QTabWidget

from src.ui.widget.widget.utils.create_geometry_widget import create_geometry_widget

class Widget(QTabWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        
        self.geometry = self.create_geometry_widget(motor_type= "axial_flux_motor_type_1")
        self.addTab(self.geometry, "Geometry")

    def create_geometry_widget(self, motor_type = "axial_flux_motor_type_1"):
        return create_geometry_widget(widget = self,
                                      motor_type= motor_type)