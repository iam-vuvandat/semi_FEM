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
            time_data = theta_data / shaft_speed
            max_time = np.max(time_data)
            if max_time < 0.1:
                return time_data * 1e3, r'Time ($ms$)'
            else:
                return time_data, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
    
    has_mrn = hasattr(record, "flux_linkage")
    has_fem = hasattr(record, "flux_linkage_fem") and show_fem

    if not has_mrn and not has_fem:
        print("\033[93mWarning: No flux linkage data found.\033[0m")
        return None, None

    phase_indices = range(n_phase) if show_all_phase else [0]
    max_h = 15

    # Cấu hình bộ màu Muted Classic theo yêu cầu
    color_r = '#B22222'  # Firebrick Red
    color_t = '#1F4E79'  # Navy Blue
    color_z = '#595959'  # Dim Gray
    
    phase_colors_muted = [color_r, color_t, color_z]

    # --- FIGURE 1: WAVEFORM (DẠNG SÓNG) ---
    fig_wave = plt.figure(figsize=(fig_width, fig_height))
    ax_wave = plt.gca()
    x_label = ""

    if has_fem:
        data_fem = record.flux_linkage_fem
        x_fem, x_label = get_x_axis(data_fem[-1, :])
        
        if show_dq:
            ax_wave.plot(x_fem, data_fem[0, :], color=color_r, linestyle='-', linewidth=2.0, label=r'$\Psi_d$ (FEM)')
            ax_wave.plot(x_fem, data_fem[1, :], color=color_t, linestyle='-', linewidth=2.0, label=r'$\Psi_q$ (FEM)')
            
        for i in phase_indices:
            color = phase_colors_muted[i % len(phase_colors_muted)]
            phase_char = chr(97 + i)
            ax_wave.plot(x_fem, data_fem[2 + i, :], color=color, linestyle='-', linewidth=1.8, 
                        label=r'$\Psi_{' + phase_char + r'}$ (FEM)')

    if has_mrn:
        data_mrn = record.flux_linkage
        x_mrn, x_label = get_x_axis(data_mrn[-1, :])
        
        mrn_linestyle = '-' if not has_fem else 'None'
        mrn_linewidth = 1.8 if not has_fem else 0
        mrn_markersize = 0 if not has_fem else 5
        
        if show_dq:
            ax_wave.plot(x_mrn, data_mrn[0, :], color=color_r, 
                        marker='o' if has_fem else None, 
                        linestyle=mrn_linestyle, linewidth=mrn_linewidth,
                        markersize=mrn_markersize, markevery=1, label=r'$\Psi_d$ (MBGRN)')
            ax_wave.plot(x_mrn, data_mrn[1, :], color=color_t, 
                        marker='s' if has_fem else None, 
                        linestyle=mrn_linestyle, linewidth=mrn_linewidth,
                        markersize=mrn_markersize, markevery=1, label=r'$\Psi_q$ (MBGRN)')
            
        for i in phase_indices:
            color = phase_colors_muted[i % len(phase_colors_muted)]
            marker = s.markers[i % len(s.markers)] if hasattr(s, 'markers') else 'o'
            phase_char = chr(97 + i)
            ax_wave.plot(x_mrn, data_mrn[2 + i, :], color=color, 
                        marker=marker if has_fem else None, 
                        linestyle=mrn_linestyle, linewidth=mrn_linewidth,
                        markersize=mrn_markersize, markevery=1, 
                        label=r'$\Psi_{' + phase_char + r'}$ (MBGRN)')

    ax_wave.set_xlabel(x_label, fontsize=s.label_size)
    ax_wave.set_ylabel(r'Flux Linkage ($Wb$)', fontsize=s.label_size)
    
    ax_wave.legend(frameon=True, loc='lower right', ncol=3, fontsize=s.legend_size)
    ax_wave.grid(True, which='major', linestyle='-', linewidth=s.grid_linewidth)
    ax_wave.margins(x=0)
    plt.tight_layout()

    # --- FIGURE 2: HARMONIC (PHỔ SÓNG HÀI) ---
    fig_harm = None
    if show_harmonic:
        color_harm_mbgrn = '#1F4E79' 
        color_harm_fem = '#B22222'   

        fig_harm = plt.figure(figsize=(fig_width, fig_height))
        ax_harm = plt.gca()
        
        if has_mrn:
            signal_mrn_a = record.flux_linkage[2, :]
            amps_mrn, _ = decompose_harmonics(signal_mrn_a, n_harmonics=max_h)
            h_orders = np.arange(len(amps_mrn))
            
            bar_offset = -0.15 if has_fem else 0
            bar_width = 0.3 if has_fem else 0.6
            
            ax_harm.bar(h_orders + bar_offset, amps_mrn, width=bar_width, color=color_harm_mbgrn, 
                        label=r'$\Psi_a$ (MBGRN)', alpha=0.9)
        
        if has_fem:
            signal_fem_a = record.flux_linkage_fem[2, :]
            amps_fem, _ = decompose_harmonics(signal_fem_a, n_harmonics=max_h)
            h_orders = np.arange(len(amps_fem))
            
            bar_offset = 0.15 if has_mrn else 0
            bar_width = 0.3 if has_mrn else 0.6
            
            ax_harm.bar(h_orders + bar_offset, amps_fem, width=bar_width, color=color_harm_fem, 
                        label=r'$\Psi_a$ (FEM)', alpha=0.8)

        ax_harm.set_xlabel('Harmonic Order', fontsize=s.label_size)
        ax_harm.set_ylabel('Amplitude (Wb)', fontsize=s.label_size)
        ax_harm.set_xticks(h_orders)
        ax_harm.legend(frameon=True, loc='upper right', fontsize=s.legend_size)
        ax_harm.grid(True, which='major', linestyle='-', linewidth=s.grid_linewidth)
        plt.tight_layout()

    if plot:
        plt.show()
        
    return fig_wave, fig_harm