import paths
from src.ui.widget.maxwell_interface.maxwell_interface import MaxwellInterface

def setup_maxwell_interface_widget(widget):
    # 1. Kiem tra doi tuong motor
    if widget.main_window.motor is None:
        from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
        widget.main_window.motor = AxialFluxMotorType1()

    # 2. Xoa tab cu neu da ton tai de giai phong bo nho
    if widget.maxwell_interface is not None:
        idx = widget.indexOf(widget.maxwell_interface)
        if idx != -1:
            widget.removeTab(idx)
        widget.maxwell_interface.deleteLater()
        widget.maxwell_interface = None

    # 3. Khoi tao lai widget MaxwellInterface moi
    widget.maxwell_interface = MaxwellInterface(parent_widget=widget)
    
    # 4. Chen vao vi tri thu 7 (index 6)
    if widget.maxwell_interface is not None:
        widget.insertTab(6, widget.maxwell_interface, "Maxwell Export")
    
    return widget.maxwell_interface