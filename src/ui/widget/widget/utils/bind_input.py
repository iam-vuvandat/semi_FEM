from PyQt5.QtWidgets import QLineEdit, QCheckBox
from PyQt5.QtCore import Qt

def bind_input(motor, attr_name, unit_factor=1e3, callback=None):
    # 1. Đọc giá trị hiện tại và kiểu dữ liệu
    original_val = getattr(motor, attr_name, 0)
    target_type = type(original_val) 
    
    # --- TRƯỜNG HỢP 1: DỮ LIỆU LOGIC (Boolean) ---
    if isinstance(original_val, bool):
        # Tạo ô tích (CheckBox)
        widget = QCheckBox()
        widget.setChecked(original_val)

        def sync_bool():
            try:
                new_val = widget.isChecked()
                setattr(motor, attr_name, new_val)
                
                # Gọi reload để cập nhật mạng từ trở/hình học
                if hasattr(motor, 'reload'):
                    motor.reload()
                
                if callback:
                    callback()
            except Exception as e:
                print(f"[Bind Error - Bool] {e}")

        # Kết nối sự kiện thay đổi trạng thái
        widget.toggled.connect(sync_bool)
        return widget

    # --- TRƯỜNG HỢP 2: DỮ LIỆU SỐ (Số nguyên/Số thực) ---
    else:
        display_val = str(original_val * unit_factor)
        edt = QLineEdit(display_val)
        edt.setFixedWidth(80)
        edt.setAlignment(Qt.AlignCenter)

        def sync_and_reload():
            try:
                raw_text = edt.text().strip()
                if not raw_text: return
                
                # Ép kiểu dựa trên target_type ban đầu (int hoặc float)
                new_val = target_type(float(raw_text) / unit_factor)
                
                setattr(motor, attr_name, new_val)
                
                if hasattr(motor, 'reload'):
                    motor.reload() 
                
                if callback:
                    callback()
            except Exception as e:
                print(f"[Bind Error - Number] {e}")
                old_val = getattr(motor, attr_name, 0)
                edt.setText(str(old_val * unit_factor))

        edt.editingFinished.connect(sync_and_reload)
        return edt