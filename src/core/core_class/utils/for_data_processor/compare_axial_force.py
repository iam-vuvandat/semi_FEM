import paths
import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from types import SimpleNamespace

def compare_axial_force(data_processor, horizontal_axis = "mechanical_position", synchronize_signal = False):
    """
    So sánh Lực dọc trục (Axial Force) giữa semi-FEM và Maxwell FEM.
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

    if hasattr(record, "mst_data") and hasattr(record, "axial_force_fem"):
        
        # 1. Chuẩn bị dữ liệu để đồng bộ hóa
        # semi-FEM: hàng index 2 là Axial Force, hàng cuối là Theta
        data_sf = np.vstack((record.mst_data[2, :], record.mst_data[-1, :]))
        
        # Maxwell FEM: hàng 0 là Force, hàng 1 là Theta
        data_fem = record.axial_force_fem.copy()
        
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
        error_peak = np.abs(peak_mrn - peak_fem) / np.abs(peak_fem) * 100 if peak_fem != 0 else 0

        average_mrn = np.mean(wave_mrn)
        average_fem = np.mean(wave_fem)
        error_average = np.abs(average_mrn - average_fem) / np.abs(average_fem) * 100 if average_fem != 0 else 0

        rms_mrn = np.sqrt(np.mean(wave_mrn**2))
        rms_fem = np.sqrt(np.mean(wave_fem**2))
        error_rms = np.abs(rms_mrn - rms_fem) / rms_fem * 100 if rms_fem != 0 else 0

        # 4. Vẽ đồ thị
        fig, ax = plt.subplots(figsize=(16, 10))

        ax.plot(x_sf, wave_mrn, color=s.colors[0], linestyle=s.linestyles[0], 
                label='Axial Force (semi-FEM)', linewidth=3.0)
        
        ax.plot(x_fem, wave_fem, color=s.colors[1], linestyle=s.linestyles[1], 
                label='Axial Force (Maxwell)', linewidth=2.5, alpha=0.8)

        # Vẽ các đường trung bình
        ax.axhline(y=average_mrn, color=s.colors[0], linestyle=':', alpha=0.6,
                   label=f'Avg semi-FEM: {average_mrn:.2f} N')
        
        ax.axhline(y=average_fem, color=s.colors[1], linestyle=':', alpha=0.6,
                   label=f'Avg Maxwell: {average_fem:.2f} N')

        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Axial Force ($N$)', fontsize=s.label_size, family=s.font_family)
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
        
        data_processor.motor.record.axial_force_compared = result
        print(f"--- Axial Force Comparison Result ---")
        print(result)
        return result

    return None