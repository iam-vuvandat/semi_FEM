from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt

def bind_input(motor, attr_name, unit_factor=1e3, callback=None):
    original_val = getattr(motor, attr_name, 0)
    target_type = type(original_val) 
    
    display_val = str(original_val * unit_factor)
    edt = QLineEdit(display_val)
    edt.setFixedWidth(80)
    edt.setAlignment(Qt.AlignCenter)

    def sync_and_reload():
        try:
            raw_text = edt.text().strip()
            if not raw_text: return
            
            new_val = target_type(float(raw_text) / unit_factor)
            
            setattr(motor, attr_name, new_val)
            motor.reload() 
            
            if callback:
                callback()
        except Exception as e:
            print(f"[Bind Error] {e}")
            old_val = getattr(motor, attr_name, 0)
            edt.setText(str(old_val * unit_factor))

    edt.editingFinished.connect(sync_and_reload)
    return edt