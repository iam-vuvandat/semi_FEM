import paths
import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from types import SimpleNamespace

def compare_torque(data_processor, horizontal_axis = "mechanical_position", synchronize_signal = False):
    """
    So sánh Mô-men điện từ (Electromagnetic Torque) giữa semi-FEM và Maxwell FEM.
    Đồng bộ hóa tín hiệu và tính toán sai số NRMSE, Peak, Average, RMS.
    """
    record = data_processor.motor.record
    s = data_processor.plot_style
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'

    # Kiểm tra dữ liệu: mst_data chứa torque semi-FEM ở index 3
    if hasattr(record, "mst_data") and hasattr(record, "torque_fem"):
        
        # 1. Chuẩn bị dữ liệu để đồng bộ hóa
        # semi-FEM: hàng 3 là Torque, hàng cuối là Theta
        data_sf = np.vstack((record.mst_data[3, :], record.mst_data[-1, :]))
        
        # Maxwell FEM: hàng 0 là Torque, hàng 1 là Theta
        # Sử dụng .copy() để bảo vệ dữ liệu gốc trong record
        data_fem = record.torque_fem.copy()
        
        if synchronize_signal:
            data_processor.synchronize_signal(data_true = data_sf, 
                                            data_pred = data_fem)
        
        # Sau khi đồng bộ, lấy trục X để vẽ
        x_sf, x_label = get_x_axis(data_sf[-1, :])
        x_fem, _ = get_x_axis(data_fem[-1, :])

        # 3. Tính toán sai số
        wave_mrn = data_sf[0, :]
        wave_fem = data_fem[0, :]

        nrmse_val = get_waveform_nrmse(data_true = wave_fem, data_pred = wave_mrn)
        
        peak_mrn = np.max(wave_mrn)
        peak_fem = np.max(wave_fem)
        error_peak = np.abs(peak_mrn - peak_fem) / peak_fem * 100

        # Quan trọng nhất: Mô-men trung bình (Average Torque)
        average_mrn = np.mean(wave_mrn)
        average_fem = np.mean(wave_fem)
        error_average = np.abs(average_mrn - average_fem) / average_fem * 100

        rms_mrn = np.sqrt(np.mean(wave_mrn**2))
        rms_fem = np.sqrt(np.mean(wave_fem**2))
        error_rms = np.abs(rms_mrn - rms_fem) / rms_fem * 100

        # 4. Vẽ đồ thị
        fig, ax = plt.subplots(figsize=(16, 10))

        # Vẽ đường mô-men tức thời
        ax.plot(x_sf, wave_mrn, color=s.colors[0], linestyle=s.linestyles[0], 
                label='Torque (semi-FEM)', linewidth=3.0)
        
        ax.plot(x_fem, wave_fem, color=s.colors[1], linestyle=s.linestyles[1], 
                label='Torque (Maxwell)', linewidth=2.5, alpha=0.8)

        # Vẽ các đường trung bình (Average lines)
        ax.axhline(y=average_mrn, color=s.colors[0], linestyle=':', alpha=0.6,
                   label=f'Avg semi-FEM: {average_mrn:.2f} Nm')
        
        ax.axhline(y=average_fem, color=s.colors[1], linestyle=':', alpha=0.6,
                   label=f'Avg Maxwell: {average_fem:.2f} Nm')

        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Torque ($N.m$)', fontsize=s.label_size, family=s.font_family)
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        ax.legend(frameon=True, loc='best', ncol=2, fontsize=s.legend_size)
        ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        
        plt.tight_layout()
        plt.show()

        # 5. Đóng gói kết quả
        result = SimpleNamespace(
            nrmse = nrmse_val, 
            peak_mrn = peak_mrn, 
            peak_fem = peak_fem,
            error_peak = error_peak,
            average_mrn = average_mrn,
            average_fem = average_fem,
            error_average = error_average,
            rms_mrn = rms_mrn,
            rms_fem = rms_fem,
            error_rms = error_rms
        )
        
        data_processor.motor.record.torque_compared = result
        print(f"--- Torque Comparison Result ---")
        print(result)
        return result

    return None