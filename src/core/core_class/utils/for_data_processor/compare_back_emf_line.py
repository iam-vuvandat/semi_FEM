import paths
import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from types import SimpleNamespace

def compare_back_emf_line(data_processor, horizontal_axis = "mechanical_position", 
                          show_all_phases = True):
    """
    So sánh Sức điện động dây (Line-to-Line Back-EMF) giữa semi-FEM và Maxwell FEM.
    Thực hiện đồng bộ hóa tín hiệu và tính toán sai số NRMSE, Peak, RMS.
    """
    record = data_processor.motor.record
    s = data_processor.plot_style
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'

    if hasattr(record, "back_emf_line") and hasattr(record, "back_emf_line_fem"):
        
        # 1. Chuẩn bị dữ liệu thô
        theta_sf = record.flux_linkage[-1, :]
        theta_fem = record.flux_linkage_fem[-1, :]
        
        # Dữ liệu MRN làm chuẩn (True)
        data_sf = np.vstack((record.back_emf_line, theta_sf))
        
        # Khởi tạo data_fem như một bản sao/mảng mới để được modify in-place
        # Việc tạo bản sao giúp tránh làm hỏng dữ liệu gốc trong record
        data_fem = np.vstack((record.back_emf_line_fem, theta_fem))
        
        # 2. Đồng bộ hóa dữ liệu (In-place modification)
        # KHÔNG gán biến ở đây vì method synchronize_signal trả về None
        data_processor.synchronize_signal(data_true = data_sf, 
                                          data_pred = data_fem)
        
        # Sau khi gọi, data_fem đã được cập nhật dữ liệu mới từ hàm synchronize_signals
        x_sf, x_label = get_x_axis(data_sf[-1, :])
        x_fem, _ = get_x_axis(data_fem[-1, :])

        # 3. Tính toán sai số dựa trên Cặp dây AB (index 0)
        wave_mrn = data_sf[0, :]
        wave_fem = data_fem[0, :]

        nrmse_val = get_waveform_nrmse(data_true = wave_fem, data_pred = wave_mrn)
        
        peak_mrn = np.max(np.abs(wave_mrn))
        peak_fem = np.max(np.abs(wave_fem))
        error_peak = np.abs(peak_mrn - peak_fem) / peak_fem * 100

        average_mrn = np.mean(np.abs(wave_mrn))
        average_fem = np.mean(np.abs(wave_fem))
        error_average = np.abs(average_mrn - average_fem) / average_fem * 100

        rms_mrn = np.sqrt(np.mean(wave_mrn**2))
        rms_fem = np.sqrt(np.mean(wave_fem**2))
        error_rms = np.abs(rms_mrn - rms_fem) / rms_fem * 100

        # 4. Vẽ đồ thị
        fig, ax = plt.subplots(figsize=(16, 10))
        
        n_lines = data_sf.shape[0] - 1 

        if show_all_phases:
            for i in range(n_lines):
                color = s.phase_colors[i % 3] if n_lines == 3 else s.colors[i % len(s.colors)]
                line_labels = ["AB", "BC", "CA"]
                label_p = f'Line {line_labels[i]}' if i < 3 else f'Line {i}'
                
                # semi-FEM (Nét liền)
                ax.plot(x_sf, data_sf[i, :], color=color, linestyle=s.linestyles[0], 
                        label=f'{label_p} (semi-FEM)', linewidth=2.0)
                
                # Maxwell FEM (Nét đứt)
                ax.plot(x_fem, data_fem[i, :], color=color, linestyle=s.linestyles[1], 
                        label=f'{label_p} (Maxwell)', linewidth=1.5, alpha=0.8)

        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Line Back EMF ($V$)', fontsize=s.label_size, family=s.font_family)
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        ax.legend(frameon=True, loc='best', ncol=2 if n_lines > 2 else 1, fontsize=s.legend_size)
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
        
        data_processor.motor.record.back_emf_line_compared = result
        print(f"--- Line Back-EMF Comparison Result ---")
        print(result)
        return result

    return None