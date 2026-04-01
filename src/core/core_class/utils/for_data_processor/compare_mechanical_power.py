import paths
import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from types import SimpleNamespace

def compare_mechanical_power(data_processor, horizontal_axis = "mechanical_position"):
    """
    So sánh Công suất cơ học (Mechanical Power) giữa semi-FEM và Maxwell FEM.
    Đồng bộ hóa tín hiệu và tính toán các chỉ số sai số NRMSE, Average, Peak.
    """
    record = data_processor.motor.record
    s = data_processor.plot_style
    shaft_speed_rpm = getattr(data_processor.motor.mechanical_data, 'shaft_speed', 3000)
    omega_m = (shaft_speed_rpm * np.pi * 2) / 60 

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / omega_m, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'

    # Kiểm tra sự tồn tại của dữ liệu công suất cơ học
    if hasattr(record, "mechanical_power") and hasattr(record, "mechanical_power_fem"):
        
        # 1. Lấy dữ liệu thô
        # Dữ liệu MRN (semi-FEM): record.mechanical_power (hàng 0: Power, hàng 1: Theta)
        data_sf_raw = record.mechanical_power
        
        # Dữ liệu Maxwell FEM: record.mechanical_power_fem (hàng 0: Power, hàng 1: Theta)
        data_fem_raw = record.mechanical_power_fem
        
        # 2. Đồng bộ hóa tín hiệu
        data_fem = data_processor.synchronize_signal(data_true = data_sf_raw, 
                                                     data_pred = data_fem_raw)
        data_sf = data_sf_raw
        
        x_sf, x_label = get_x_axis(data_sf[-1, :])
        x_fem, _ = get_x_axis(data_fem[-1, :])

        # 3. Tính toán sai số
        wave_mrn = data_sf[0, :]
        wave_fem = data_fem[0, :]

        nrmse_val = get_waveform_nrmse(data_true = wave_fem, data_pred = wave_mrn)
        
        peak_mrn = np.max(wave_mrn)
        peak_fem = np.max(wave_fem)
        error_peak = np.abs(peak_mrn - peak_fem) / peak_fem * 100

        average_mrn = np.mean(wave_mrn)
        average_fem = np.mean(wave_fem)
        error_average = np.abs(average_mrn - average_fem) / average_fem * 100

        rms_mrn = np.sqrt(np.mean(wave_mrn**2))
        rms_fem = np.sqrt(np.mean(wave_fem**2))
        error_rms = np.abs(rms_mrn - rms_fem) / rms_fem * 100

        # 4. Vẽ đồ thị
        fig, ax = plt.subplots(figsize=(16, 10))

        # Vẽ đường công suất tức thời
        ax.plot(x_sf, wave_mrn, color=s.colors[0], linestyle=s.linestyles[0], 
                label='Mech Power (semi-FEM)', linewidth=3.0)
        
        ax.plot(x_fem, wave_fem, color=s.colors[1], linestyle=s.linestyles[1], 
                label='Mech Power (Maxwell)', linewidth=2.5, alpha=0.8)

        # Vẽ đường trung bình
        ax.axhline(y=average_mrn, color=s.colors[0], linestyle=':', alpha=0.6,
                   label=f'Avg semi-FEM: {average_mrn:.2f} W')
        
        ax.axhline(y=average_fem, color=s.colors[1], linestyle=':', alpha=0.6,
                   label=f'Avg Maxwell: {average_fem:.2f} W')

        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Mechanical Power ($W$)', fontsize=s.label_size, family=s.font_family)
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        ax.legend(frameon=True, loc='best', ncol=2, fontsize=s.legend_size)
        ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        
        plt.tight_layout()
        plt.show()

        # 5. Lưu kết quả vào record
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
        
        data_processor.motor.record.mechanical_power_compared = result
        print(f"--- Mechanical Power Comparison Result ---")
        print(result)
        return result

    return None