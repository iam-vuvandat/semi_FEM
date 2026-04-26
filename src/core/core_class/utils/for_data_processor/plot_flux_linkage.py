import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.decompose_harmonics import decompose_harmonics

def plot_flux_linkage(data_processor, 
                      horizontal_axis = "mechanical_position", 
                      show_fem = True, 
                      show_dq = False, 
                      show_all_phase = False,
                      show_harmonic = True, 
                      plot = False):
    
    if not plot:
        return
        
    motor = data_processor.motor
    record = motor.record
    n_phase = motor.winding_data.phase
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60
    s = data_processor.plot_style

    # Cấu hình kích thước theo tỉ lệ vàng
    fig_width = 14
    fig_height = fig_width / 1.618

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
    
    has_mrn = hasattr(record, "flux_linkage")
    has_fem = hasattr(record, "flux_linkage_fem") and show_fem

    if not has_mrn and not has_fem:
        print("\033[93mWarning: No flux linkage data found.\033[0m")
        return

    phase_indices = range(n_phase) if show_all_phase else [0]
    max_h = 15

    # --- FIGURE 1: WAVEFORM (DẠNG SÓNG) ---
    plt.figure(figsize=(fig_width, fig_height))
    ax_wave = plt.gca()
    x_label = ""

    if has_fem:
        data_fem = record.flux_linkage_fem
        x_fem, x_label = get_x_axis(data_fem[-1, :])
        
        if show_dq:
            ax_wave.plot(x_fem, data_fem[0, :], color='black', linestyle='-', linewidth=3.5, label=r'$\Psi_d$ (FEM)')
            ax_wave.plot(x_fem, data_fem[1, :], color='black', linestyle='-', linewidth=3.5, label=r'$\Psi_q$ (FEM)')
            
        for i in phase_indices:
            color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
            phase_char = chr(97 + i)
            ax_wave.plot(x_fem, data_fem[2 + i, :], color=color, linestyle='-', linewidth=2.5, 
                        label=r'$\Psi_{' + phase_char + r'}$ (FEM)')

    if has_mrn:
        data_mrn = record.flux_linkage
        x_mrn, x_label = get_x_axis(data_mrn[-1, :])
        
        if show_dq:
            ax_wave.plot(x_mrn, data_mrn[0, :], color='black', marker=s.markers[0], linestyle='None', 
                        markevery=max(1, len(x_mrn)//20), label=r'$\Psi_d$ (MRN)')
            ax_wave.plot(x_mrn, data_mrn[1, :], color='black', marker=s.markers[1], linestyle='None', 
                        markevery=max(1, len(x_mrn)//20), label=r'$\Psi_q$ (MRN)')
            
        for i in phase_indices:
            color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
            marker = s.markers[i % len(s.markers)]
            phase_char = chr(97 + i)
            ax_wave.plot(x_mrn, data_mrn[2 + i, :], color=color, marker=marker, linestyle='None', 
                        markersize=10, markevery=max(1, len(x_mrn)//15), 
                        label=r'$\Psi_{' + phase_char + r'}$ (MRN)')

    ax_wave.set_xlabel(x_label, fontsize=s.label_size)
    ax_wave.set_ylabel(r'Flux Linkage ($Wb$)', fontsize=s.label_size)
    ax_wave.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
    ax_wave.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
    plt.tight_layout()

    # --- FIGURE 2: HARMONIC (PHỔ SÓNG HÀI) ---
    if show_harmonic:
        color_mrn = '#4477AA' # Blue
        color_fem = '#EE6677' # Red

        plt.figure(figsize=(fig_width, fig_height))
        ax_harm = plt.gca()
        
        if has_mrn:
            signal_mrn_a = record.flux_linkage[2, :]
            amps_mrn, _ = decompose_harmonics(signal_mrn_a, n_harmonics=max_h)
            h_orders = np.arange(len(amps_mrn))
            ax_harm.bar(h_orders - 0.15, amps_mrn, width=0.3, color=color_mrn, 
                        label=r'$\Psi_a$ (MRN)', alpha=0.9)
        
        if has_fem:
            signal_fem_a = record.flux_linkage_fem[2, :]
            amps_fem, _ = decompose_harmonics(signal_fem_a, n_harmonics=max_h)
            h_orders = np.arange(len(amps_fem))
            ax_harm.bar(h_orders + 0.15, amps_fem, width=0.3, color=color_fem, 
                        label=r'$\Psi_a$ (FEM)', alpha=0.8)

        ax_harm.set_xlabel('Harmonic Order', fontsize=s.label_size)
        ax_harm.set_ylabel('Amplitude (Wb)', fontsize=s.label_size)
        ax_harm.set_xticks(h_orders)
        ax_harm.legend(frameon=True, loc='upper right', fontsize=s.legend_size)
        ax_harm.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        plt.tight_layout()

    plt.show()