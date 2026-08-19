import paths
from PyQt5.QtWidgets import QTabWidget

from src.ui.widget.widget.utils.setup_geometry_widget import setup_geometry_widget
from src.ui.widget.widget.utils.setup_winding_widget import setup_winding_widget
from src.ui.widget.widget.utils.setup_input_data_widget import setup_input_data_widget
from src.ui.widget.widget.utils.setup_mesh_widget import setup_mesh_widget
from src.ui.widget.widget.utils.setup_calculation_widget import setup_calculation_widget
from src.ui.widget.widget.utils.setup_result_widget import setup_result_widget
from src.ui.widget.widget.utils.setup_maxwell_interface_widget import setup_maxwell_interface_widget

class Widget(QTabWidget):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window

        self.geometry_tab = None
        self.winding_tab = None
        self.input_data_tab = None
        self.mesh_tab = None
        self.calculation_tab = None
        self.result_tab = None
        self.maxwell_interface = None

        self.geometry_tab = self.setup_geometry_widget()
        self.winding_tab = self.setup_winding_widget()
        self.input_data_tab = self.setup_input_data_widget()
        self.mesh_tab = self.setup_mesh_widget()
        self.calculation_tab = self.setup_calculation_widget()
        self.result_tab = self.setup_result_widget()
        self.maxwell_interface = self.setup_maxwell_interface_widget()
        
        self.currentChanged.connect(self.on_tab_changed)
    
    def on_tab_changed(self, index):
        current_tab = self.widget(index)
        if hasattr(current_tab, "refresh"):
            current_tab.refresh()
    
    def setup_geometry_widget(self):
        return setup_geometry_widget(widget=self)   
    
    def setup_winding_widget(self):
        return setup_winding_widget(widget=self)
    
    def setup_input_data_widget(self):
        return setup_input_data_widget(widget=self)
    
    def setup_mesh_widget(self):
        return setup_mesh_widget(widget=self)
    
    def setup_calculation_widget(self):
        return setup_calculation_widget(widget=self)
    
    def setup_result_widget(self):
        return setup_result_widget(widget=self)
    
    def setup_maxwell_interface_widget(self):
        return setup_maxwell_interface_widget(widget=self)