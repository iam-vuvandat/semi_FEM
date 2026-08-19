import paths
from PyQt5.QtWidgets import QWidget
from src.ui.widget.geometry.init_ui import init_ui

class Geometry(QWidget):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.main_window = self.parent_widget.main_window
        
        self.motor_type_combo = None
        self.plotter = None
        
        self.init_ui()

    def init_ui(self):
        return init_ui(geometry_tab=self)

    def refresh(self):
        motor = self.main_window.motor
        if motor:
            motor.require("geometry")
            if hasattr(self, "refresh_plot") and callable(self.refresh_plot):
                self.refresh_plot()