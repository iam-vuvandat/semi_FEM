import paths
from src.ui.widget.geometry.geometry_for_axial_flux_motor_type_1.geometry_for_axial_flux_motor_type_1 import GeometryForAxialFluxType1

def setup_geometry_widget(widget, motor_type):
    # Sử dụng tên mới geometry_tab để không bị trùng với hàm .geometry() của Qt
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