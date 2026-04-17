import numpy as np 
pi = np.pi

from types import SimpleNamespace

def calculate_mechanical_power(torque_data, speed_rpm):
    speed_rad_s = speed_rpm * 2 * pi / 60
    mechanical_power = torque_data.copy()
    
    # Nhan tat ca cac hang du lieu (tru hang cuoi cung) voi toc do goc
    mechanical_power[:-1, :] *= speed_rad_s
    
    # Tinh toan cong suat co hoc trung binh tu hang du lieu dau tien
    average_mechanical_power = np.mean(mechanical_power[0, :])

    return SimpleNamespace(
        mechanical_data = mechanical_power, 
        average_mechanical_data = average_mechanical_power
    )