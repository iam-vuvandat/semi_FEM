import paths
from PyQt5.QtWidgets import QWidget
from src.ui.widget.input_data.init_ui import init_ui

class InputData(QWidget):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.main_window = self.parent_widget.main_window
        
        self.summary_display = None
        
        self.init_ui()

    def init_ui(self):
        return init_ui(input_tab=self)

    def refresh(self):
        motor = self.main_window.motor
        if motor:
            motor.require("material_database")
            if hasattr(self, 'refresh_content') and callable(self.refresh_content):
                self.refresh_content()