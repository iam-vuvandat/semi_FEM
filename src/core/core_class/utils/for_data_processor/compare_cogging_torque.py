import paths
import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from types import SimpleNamespace

def compare_cogging_torque(data_processor, horizontal_axis = "mechanical_position", synchronize_signal = False):
    """
    So sánh Mô-men răng khía (Cogging Torque) giữa semi-FEM và Maxwell FEM.
    """
    record = data_processor.motor.record
    s = data_processor.plot_style
    # Chú ý: shaft_speed nên lấy từ mechanical_data để đảm bảo chính xác
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'

    # SỬA: Kiểm tra đúng các biến liên quan đến Cogging
    if hasattr(record, "cogging") and hasattr(record, "cogging_fem"):
        
        # SỬA: Lấy từ record.cogging (hàng 0 là torque, hàng 1 là vị trí)
        data_sf = record.cogging.copy()
        
        # SỬA: Lấy đúng record.cogging_fem từ Maxwell export
        data_fem = record.cogging_fem.copy()
        
        if synchronize_signal:
            data_processor.synchronize_signal(data_true = data_sf, 
                                            data_pred = data_fem)
        
        # Lấy trục X
        x_sf, x_label = get_x_axis(data_sf[-1, :])
        x_fem, _ = get_x_axis(data_fem[-1, :])

        wave_mrn = data_sf[0, :]
        wave_fem = data_fem[0, :]

        # Tính toán sai số
        nrmse_val = get_waveform_nrmse(data_true = wave_fem, data_pred = wave_mrn)
        
        peak_mrn = np.max(np.abs(wave_mrn)) # Cogging thường lấy trị tuyệt đối đỉnh
        peak_fem = np.max(np.abs(wave_fem))
        
        # Tránh chia cho 0 nếu peak_fem cực nhỏ
        denom = peak_fem if peak_fem > 1e-9 else 1e-9
        error_peak = np.abs(peak_mrn - peak_fem) / denom * 100

        average_mrn = np.mean(wave_mrn)
        average_fem = np.mean(wave_fem)

        rms_mrn = np.sqrt(np.mean(wave_mrn**2))
        rms_fem = np.sqrt(np.mean(wave_fem**2))

        # Vẽ đồ thị
        fig, ax = plt.subplots(figsize=(12, 7)) # Resize lại cho cân đối

        ax.plot(x_sf, wave_mrn, color=s.colors[0], linestyle=s.linestyles[0], 
                label='Cogging (3D-MBGRN)', linewidth=2.5)
        
        ax.plot(x_fem, wave_fem, color=s.colors[1], linestyle=s.linestyles[1], 
                label='Cogging (Maxwell)', linewidth=2.0, alpha=0.8)

        ax.set_xlabel(x_label, fontsize=s.label_size)
        ax.set_ylabel(r'Cogging Torque ($N.m$)', fontsize=s.label_size)
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        ax.legend(frameon=True, loc='best', fontsize=s.legend_size)
        ax.grid(True, which='both', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.show()

        # Đóng gói kết quả vào cogging_compared
        result = SimpleNamespace(
            nrmse = nrmse_val, 
            peak_mrn = peak_mrn, 
            peak_fem = peak_fem,
            error_peak = error_peak,
            average_mrn = average_mrn,
            average_fem = average_fem,
            rms_mrn = rms_mrn,
            rms_fem = rms_fem
        )
        
        record.cogging_compared = result
        print(f"--- Cogging Torque Comparison Result ---")
        print(f"NRMSE: {nrmse_val:.4f}")
        print(f"Peak Error: {error_peak:.2f}%")
        return result

    print("Warning: Missing cogging data in record for comparison.")
    return None