import paths
from src.ui.widget.input_data.input_data import InputData

def setup_input_data_widget(widget):
    """
    Dọn dẹp tab Input Data cũ và khởi tạo tab mới tại index 2.
    Thứ tự tab: Geometry (0) -> Winding (1) -> Input Data (2)
    """
    # Dọn dẹp tab cũ nếu đã tồn tại
    if hasattr(widget, 'input_data_tab') and widget.input_data_tab is not None:
        index = widget.indexOf(widget.input_data_tab)
        if index != -1:
            widget.removeTab(index)
        
        widget.input_data_tab.deleteLater()
        widget.input_data_tab = None

    # Khởi tạo instance mới
    widget.input_data_tab = InputData(parent_widget=widget)

    # Chèn vào vị trí thứ 3 trong thanh Tab
    if widget.input_data_tab is not None:
        widget.insertTab(2, widget.input_data_tab, "Input Data")
        
    return widget.input_data_tab