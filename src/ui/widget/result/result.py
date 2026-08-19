from PyQt5.QtWidgets import QWidget
from src.ui.widget.result.init_ui import init_ui

class Result(QWidget):
    def __init__(self, parent_widget=None):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.main_window = parent_widget.main_window if parent_widget else None
        
        self.status_label = None
        self.refresh = None
        
        init_ui(self)