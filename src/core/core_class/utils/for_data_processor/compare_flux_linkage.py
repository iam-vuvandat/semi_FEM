import paths
import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from types import SimpleNamespace

def compare_flux_linkage(data_processor, horizontal_axis = "mechanical_position", 
                         show_dq_axis = False, show_all_phases = True):
    record = data_processor.motor.record
    n_phase = data_processor.motor.winding_data.phase
    s = data_processor.plot_style
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'

    if hasattr(record, "flux_linkage") and hasattr(record, "flux_linkage_fem"):
        # 1. Lấy dữ liệu thô
        data_sf = record.flux_linkage
        data_fem_raw = record.flux_linkage_fem
        
        # 2. Đồng bộ hóa dữ liệu
        data_fem = data_processor.synchronize_signal(data_true = data_sf, 
                                                     data_pred = data_fem_raw)
        
        x_sf, x_label = get_x_axis(data_sf[-1, :])
        x_fem, _ = get_x_axis(data_fem[-1, :])

        # 3. Tính toán sai số dựa trên Pha A (index 2)
        wave_mrn = data_sf[2, :]
        wave_fem = data_fem[2, :]

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

        if show_dq_axis:
            ax.plot(x_sf, data_sf[0, :], color='#4477AA', linestyle=s.linestyles[0], 
                    label=r'$\Psi_d$ (semi-FEM)', linewidth=3.0)
            ax.plot(x_fem, data_fem[0, :], color='#4477AA', linestyle=s.linestyles[1], 
                    label=r'$\Psi_d$ (Maxwell)', linewidth=2.0, alpha=0.7)

            ax.plot(x_sf, data_sf[1, :], color='#EE6677', linestyle=s.linestyles[0], 
                    label=r'$\Psi_q$ (semi-FEM)', linewidth=3.0)
            ax.plot(x_fem, data_fem[1, :], color='#EE6677', linestyle=s.linestyles[1], 
                    label=r'$\Psi_q$ (Maxwell)', linewidth=2.0, alpha=0.7)

        if show_all_phases:
            for i in range(n_phase):
                color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
                label_p = f'Phase {chr(65+i)}'
                ax.plot(x_sf, data_sf[2 + i, :], color=color, linestyle=s.linestyles[0], 
                        label=f'{label_p} (semi-FEM)', linewidth=2.0)
                ax.plot(x_fem, data_fem[2 + i, :], color=color, linestyle=s.linestyles[1], 
                        label=f'{label_p} (Maxwell)', linewidth=1.5, alpha=0.8)

        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Flux Linkage ($Wb$)', fontsize=s.label_size, family=s.font_family)
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        ax.legend(frameon=True, loc='best', ncol=2 if (n_phase > 3 or show_dq_axis) else 1, 
                  fontsize=s.legend_size)
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
        
        data_processor.motor.record.flux_linkage_compared = result
        print(result)
        return result

    return None