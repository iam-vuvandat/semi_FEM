import paths
from src.ui.widget.result.result import Result

def setup_result_widget(widget):
    if widget.main_window.motor is None:
        from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
        widget.main_window.motor = AxialFluxMotorType1()

    if widget.result_tab is not None:
        idx = widget.indexOf(widget.result_tab)
        if idx != -1:
            widget.removeTab(idx)
        widget.result_tab.deleteLater()
        widget.result_tab = None

    widget.result_tab = Result(parent_widget=widget)
    
    if widget.result_tab is not None:
        widget.insertTab(5, widget.result_tab, "Result")
    
    return widget.result_tab