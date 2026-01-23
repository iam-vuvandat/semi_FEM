import paths
from PyQt5.QtWidgets import QTabWidget

from src.ui.widget.widget.utils.setup_geometry_widget import setup_geometry_widget
from src.ui.widget.widget.utils.setup_winding_widget import setup_winding_widget
from src.ui.widget.widget.utils.setup_input_data_widget import setup_input_data_widget

class Widget(QTabWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.geometry_tab = None
        self.geometry_tab = self.setup_geometry_widget(motor_type= "axial_flux_motor_type_1")

        self.winding_tab = None
        self.winding_tab = self.setup_winding_widget()

        self.input_data_tab = None
        self.input_data_tab = self.setup_input_data_widget()
    
    def setup_geometry_widget(self, motor_type = "axial_flux_motor_type_1"):
        return setup_geometry_widget(widget = self,
                                    motor_type= motor_type)   
    
    def setup_winding_widget(self):
        return setup_winding_widget(widget= self)
    
    def setup_input_data_widget(self):
        return setup_input_data_widget(widget = self)