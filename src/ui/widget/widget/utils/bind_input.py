from PyQt5.QtWidgets import QLineEdit, QCheckBox
from PyQt5.QtCore import Qt

def bind_input(motor, attr_name, unit_factor=1e3, callback=None):
    # 1. Đọc giá trị hiện tại và kiểu dữ liệu
    original_val = getattr(motor, attr_name)
    target_type = type(original_val) 
    
    # --- TRƯỜNG HỢP 1: DỮ LIỆU LOGIC (Boolean) ---
    if isinstance(original_val, bool):
        widget = QCheckBox()
        widget.setChecked(original_val)

        def sync_bool():
            new_val = widget.isChecked()
            setattr(motor, attr_name, new_val)
            
            # Kích hoạt hàm điều khiển bên ngoài
            if callback:
                callback()

        widget.toggled.connect(sync_bool)
        return widget

    # --- TRƯỜNG HỢP 2: DỮ LIỆU SỐ (Số nguyên/Số thực) ---
    else:
        display_val = str(original_val * unit_factor)
        edt = QLineEdit(display_val)
        edt.setFixedWidth(80)
        edt.setAlignment(Qt.AlignCenter)

        def sync_and_callback():
            raw_text = edt.text().strip()
            if not raw_text: return
            
            # Ép kiểu dựa trên target_type ban đầu
            new_val = target_type(float(raw_text) / unit_factor)
            setattr(motor, attr_name, new_val)
            
            # Kích hoạt hàm điều khiển bên ngoài
            if callback:
                callback()

        edt.editingFinished.connect(sync_and_callback)
        return edt