import paths
from src.ui.widget.calculation.calculation import Calculation

def setup_calculation_widget(widget):
    # 1. Kiem tra doi tuong motor
    if widget.main_window.motor is None:
        from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
        widget.main_window.motor = AxialFluxMotorType1()

    # 2. Xoa tab cu neu da ton tai de giai phong bo nho
    # Gia su tab Calculation nam o vi tri cuoi cung (index 4)
    if widget.calculation_tab is not None:
        # Tim index hien tai cua calculation_tab de remove cho chinh xac
        idx = widget.indexOf(widget.calculation_tab)
        if idx != -1:
            widget.removeTab(idx)
        widget.calculation_tab.deleteLater()
        widget.calculation_tab = None

    # 3. Khoi tao lai widget Calculation moi
    widget.calculation_tab = Calculation(parent_widget=widget)
    
    # 4. Chen lai vao thanh TabWidget
    if widget.calculation_tab is not None:
        widget.addTab(widget.calculation_tab, "Calculation")
    
    return widget.calculation_tab