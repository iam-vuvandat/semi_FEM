import paths
from src.ui.widget.geometry.geometry_for_axial_flux_motor_type_1.geometry_for_axial_flux_motor_type_1 import GeometryForAxialFluxType1

def setup_geometry_widget(widget):
    if widget.main_window.motor is not None:
        motor_type = widget.main_window.motor.motor_type
    else:
        motor_type = "axial_flux_motor_type_1"

    if widget.geometry_tab is not None:
        widget.removeTab(0)
        widget.geometry_tab.deleteLater()
        widget.geometry_tab = None

    if motor_type == "axial_flux_motor_type_1":
        widget.geometry_tab = GeometryForAxialFluxType1(parent_widget=widget)
    
    if widget.geometry_tab is not None:
        widget.insertTab(0, widget.geometry_tab, "Geometry")
        widget.setCurrentIndex(0)
    
    return widget.geometry_tab