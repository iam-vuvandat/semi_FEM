import math
import numpy as np

pi = math.pi

def update_maxwell_settings(motor):
    motor.require("mechanical")
    functions = []
    
    # Trich xuat du lieu tu motor
    winding_data = motor.winding_data
    geometry_data = motor.geometry_data
    mechanical = motor.mechanical
    drive_data = motor.drive_data
    
    # Cac thong so co ban
    i_rms = drive_data.i_rms
    phase_advanced = drive_data.phase_advanced
    phase_number = winding_data.phase
    pole_pairs = int(geometry_data.rotor.pole_number // 2)
    
    # Tinh toan thong so dong dien
    i_peak = i_rms * math.sqrt(2)
    speed_rpm = getattr(mechanical, 'speed_rpm', 3000)
    omega_e = (speed_rpm * 2 * pi / 60) * pole_pairs
    beta_rad = math.radians(phase_advanced)
    
    # Tao chuoi phuong trinh cho tung pha
    for k in range(int(phase_number)):
        angle_shift = (2 * pi * k) / phase_number
        # Phi phan anh dung phep bien doi Park nguoc trong Drive
        phi = beta_rad + angle_shift 
        func_str = f"{round(i_peak, 4)} * cos({round(omega_e, 4)} * Time + {round(phi, 4)})A"
        functions.append(func_str)
        
    motor.maxwell_export_option.current_function = functions

# --- Script Test ---
if __name__ == "__main__":
    # Tao cau truc lop gia lap (Mock) de khop voi yeu cau cua ham
    class MockObject:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
        def require(self, name):
            if not hasattr(self, name):
                raise AttributeError(f"Missing required attribute: {name}")

    # Khoi tao cac thanh phan con
    mock_winding = MockObject(phase=3)
    mock_rotor = MockObject(pole_number=8)
    mock_geometry = MockObject(rotor=mock_rotor)
    mock_mechanical = MockObject(speed_rpm=3000)
    mock_drive = MockObject(i_rms=10.0, phase_advanced=30.0)
    mock_export = MockObject(current_function=[])

    # Khoi tao doi tuong motor tong the
    motor_test = MockObject(
        winding_data=mock_winding,
        geometry_data=mock_geometry,
        mechanical=mock_mechanical,
        drive_data=mock_drive,
        maxwell_export_option=mock_export
    )

    # Thuc thi ham
    update_maxwell_settings(motor_test)

    # In ket qua kiem tra
    print("--- Maxwell Current Functions Export ---")
    for i, func in enumerate(motor_test.maxwell_export_option.current_function):
        print(f"Phase {i}: {func}")