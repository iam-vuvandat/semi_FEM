import os
import paths
import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.decompose_harmonics import decompose_harmonics

def plot_airgap_flux_density_no_load(data_processor, 
                                     horizontal_axis="mechanical_position", 
                                     show_fem=True, 
                                     show_harmonic=True,
                                     plot=False):
    
    root_dir = paths.configure_path()
    figure_dir = os.path.join(root_dir, "data", "repo", "figures")
    if not os.path.exists(figure_dir):
        os.makedirs(figure_dir)

    motor = data_processor.motor
    record = motor.record
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    s = data_processor.plot_style

    fig_width = 14
    fig_height = fig_width / 1.618

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time Equivalent ($s$)'
        else:
            return theta_data, r'Angular Position ($rad$)'
    
    has_mrn = hasattr(record, "airgap_flux_density_no_load")
    has_fem = hasattr(record, "airgap_flux_density_no_load_fem") and show_fem

    fig_wave = plt.figure(figsize=(fig_width, fig_height))
    ax = plt.gca()
    x_label = ""

    color_r = '#B22222'  
    color_t = '#1F4E79'  
    color_z = '#595959'  

    if has_fem:
        data_fem = record.airgap_flux_density_no_load_fem
        x_fem, x_label = get_x_axis(data_fem[4, :])
        
        ax.plot(x_fem, data_fem[0, :], color=color_r, linestyle='-', linewidth=1.2, label=r'$B_r$ (FEM)')
        ax.plot(x_fem, data_fem[1, :], color=color_t, linestyle='-', linewidth=1.2, label=r'$B_t$ (FEM)')
        ax.plot(x_fem, data_fem[2, :], color=color_z, linestyle='-', linewidth=1.2, label=r'$B_z$ (FEM)')

    if has_mrn:
        data_mrn = record.airgap_flux_density_no_load
        x_mrn, x_label = get_x_axis(data_mrn[4, :])
        
        ax.plot(x_mrn, data_mrn[0, :], color=color_r, linestyle='None', marker='o', markersize=4, markevery=1, label=r'$B_r$ (MBGRN)')
        ax.plot(x_mrn, data_mrn[1, :], color=color_t, linestyle='None', marker='s', markersize=4, markevery=1, label=r'$B_t$ (MBGRN)')
        ax.plot(x_mrn, data_mrn[2, :], color=color_z, linestyle='None', marker='^', markersize=4, markevery=1, label=r'$B_z$ (MBGRN)')

    ax.set_xlabel(x_label, fontsize=s.label_size)
    ax.set_ylabel('Airgap Flux Density (T)', fontsize=s.label_size)
    
    ax.legend(frameon=True, loc='upper right', fontsize=s.legend_size, ncol=2)
    ax.grid(True, which='major', linestyle='-', linewidth=s.grid_linewidth)
    ax.margins(x=0)
    
    plt.tight_layout()
    
    wave_path = os.path.join(figure_dir, "airgap_flux_density_no_load_waveform.png")
    fig_wave.savefig(wave_path, bbox_inches='tight', dpi=300)

    fig_harm = None
    if show_harmonic:
        max_h = 15
        color_harm_mbgrn = '#1F4E79' 
        color_harm_fem = '#B22222'   

        components = [
            {"idx": 0, "label_mrn": r'$B_r$ (MBGRN)', "label_fem": r'$B_r$ (FEM)', "title": "Radial Component ($B_r$)", "unit": "mT", "scale": 1e3},
            {"idx": 1, "label_mrn": r'$B_t$ (MBGRN)', "label_fem": r'$B_t$ (FEM)', "title": "Tangential Component ($B_t$)", "unit": "T", "scale": 1.0},
            {"idx": 2, "label_mrn": r'$B_z$ (MBGRN)', "label_fem": r'$B_z$ (FEM)', "title": "Axial Component ($B_z$)", "unit": "T", "scale": 1.0}
        ]

        fig_harm, axs = plt.subplots(3, 1, figsize=(fig_width, fig_height * 2.2), sharex=True)
        
        for i, comp in enumerate(components):
            ax_harm = axs[i]
            idx = comp["idx"]
            scale = comp["scale"]
            
            if has_mrn:
                signal_mrn = record.airgap_flux_density_no_load[idx, :]
                amps_mrn, _ = decompose_harmonics(signal_mrn, n_harmonics=max_h)
                h_orders = np.arange(len(amps_mrn))
                
                bar_offset = -0.15 if has_fem else 0
                bar_width = 0.3 if has_fem else 0.6
                
                ax_harm.bar(h_orders + bar_offset, amps_mrn * scale, width=bar_width, color=color_harm_mbgrn, 
                            label=comp["label_mrn"], alpha=0.9)
            
            if has_fem:
                signal_fem = record.airgap_flux_density_no_load_fem[idx, :]
                amps_fem, _ = decompose_harmonics(signal_fem, n_harmonics=max_h)
                h_orders = np.arange(len(amps_fem))
                
                bar_offset = 0.15 if has_mrn else 0
                bar_width = 0.3 if has_fem else 0.6
                
                ax_harm.bar(h_orders + bar_offset, amps_fem * scale, width=bar_width, color=color_harm_fem, 
                            label=comp["label_fem"], alpha=0.8)

            ax_harm.set_ylabel(f'Amplitude ({comp["unit"]})', fontsize=s.label_size)
            ax_harm.set_title(comp["title"], fontsize=s.label_size, pad=5)
            ax_harm.legend(frameon=True, loc='upper right', fontsize=s.legend_size)
            ax_harm.grid(True, which='major', linestyle='-', linewidth=s.grid_linewidth)
            
            ax_harm.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{x:.2f}"))
        
        axs[-1].set_xlabel('Harmonic Order', fontsize=s.label_size)
        axs[-1].set_xticks(h_orders)
        
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.3)
        
        harm_path = os.path.join(figure_dir, "airgap_flux_density_no_load_harmonics.png")
        fig_harm.savefig(harm_path, bbox_inches='tight', dpi=300)

    if plot:
        plt.show()
        
    return fig_wave, fig_harm