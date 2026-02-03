import paths
from PyQt5.QtWidgets import QWidget
from src.ui.widget.calculation.init_ui import init_ui

class Calculation(QWidget):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.main_window = self.parent_widget.main_window
        self.motor = self.main_window.motor
        
        self.btn_run = None
        self.progress_bar = None
        self.log_console = None
        
        self.init_ui()

    def init_ui(self):
        return init_ui(calculation_tab=self)

    def run_solver(self):
        self.log_console.append("<b style='color: #4CAF50;'>[System] Starting 3D-MBGRN Analysis...</b>")
        self.progress_bar.setValue(10)
        
        try:
            # Goi method analysis_motor ma ban da cung cap
            # Do calculation_data da duoc update qua bind_input, solver se lay truc tiep tu motor
            result = self.motor.analysis_motor()
            
            self.progress_bar.setValue(100)
            self.log_console.append("<b style='color: #4CAF50;'>[System] Success. Data recorded.</b>")
            return result
            
        except Exception as e:
            self.log_console.append(f"<b style='color: #F44336;'>[Error] {str(e)}</b>")
            self.progress_bar.setValue(0)

    def refresh_tab(self):
        if hasattr(self, 'log_console') and self.log_console:
            from src.ui.widget.calculation.init_ui import update_calculation_inputs
            update_calculation_inputs(self, self.main_window.motor)