import paths
import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from types import SimpleNamespace

def compare_back_emf(data_processor, horizontal_axis = "mechanical_position", 
                     show_all_phases = True):
    record = data_processor.motor.record
    n_phase = data_processor.motor.winding_data.phase
    s = data_processor.plot_style
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'

    # Kiểm tra sự tồn tại của dữ liệu Back-EMF và dữ liệu Flux (để lấy trục tọa độ theta)
    if hasattr(record, "back_emf") and hasattr(record, "back_emf_fem"):
        
        # 1. Chuẩn bị dữ liệu để đồng bộ hóa
        # Lấy trục theta từ flux_linkage (SF và FEM)
        theta_sf = record.flux_linkage[-1, :]
        theta_fem = record.flux_linkage_fem[-1, :]
        
        # Khởi tạo mảng dữ liệu (np.vstack tạo ra mảng mới, an toàn để modify)
        data_sf = np.vstack((record.back_emf, theta_sf))
        data_fem = np.vstack((record.back_emf_fem, theta_fem))
        
        # 2. Đồng bộ hóa dữ liệu (In-place modification)
        # Không gán biến vì method synchronize_signal trả về None
        data_processor.synchronize_signal(data_true = data_sf, 
                                          data_pred = data_fem)
        
        # Sau khi gọi, data_fem đã được cập nhật dữ liệu mới từ hàm synchronize_signals
        x_sf, x_label = get_x_axis(data_sf[-1, :])
        x_fem, _ = get_x_axis(data_fem[-1, :])

        # 3. Tính toán sai số dựa trên Pha A (index 0)
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

        if show_all_phases:
            for i in range(n_phase):
                color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
                label_p = f'Phase {chr(65+i)}'
                
                # semi-FEM (Nét liền)
                ax.plot(x_sf, data_sf[i, :], color=color, linestyle=s.linestyles[0], 
                        label=f'{label_p} (semi-FEM)', linewidth=2.0)
                
                # Maxwell FEM (Nét đứt)
                ax.plot(x_fem, data_fem[i, :], color=color, linestyle=s.linestyles[1], 
                        label=f'{label_p} (Maxwell)', linewidth=1.5, alpha=0.8)

        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Back EMF ($V$)', fontsize=s.label_size, family=s.font_family)
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        ax.legend(frameon=True, loc='best', ncol=2 if n_phase > 3 else 1, fontsize=s.legend_size)
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
        
        data_processor.motor.record.back_emf_compared = result
        print(f"--- Back-EMF Comparison Result ---")
        print(result)
        return result

    return None