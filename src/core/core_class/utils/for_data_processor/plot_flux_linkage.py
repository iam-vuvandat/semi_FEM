import numpy as np 
import matplotlib.pyplot as plt

def plot_flux_linkage(data_processor, 
                      horizontal_axis = "mechanical_position", 
                      show_fem = True, 
                      show_dq = False, 
                      show_all_phase = False, 
                      plot = False):
    
    if not plot:
        return
        
    motor = data_processor.motor
    record = motor.record
    n_phase = motor.winding_data.phase
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    s = data_processor.plot_style

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
    
    has_sf = hasattr(record, "flux_linkage")
    has_fem = hasattr(record, "flux_linkage_fem") and show_fem

    if not has_sf and not has_fem:
        print("\033[93mWarning: No flux linkage data found.\033[0m")
        return

    fig, ax = plt.subplots(figsize=(16, 10))
    x_label = ""
    phase_indices = range(n_phase) if show_all_phase else [0]

    if has_fem:
        data_fem = record.flux_linkage_fem
        x_fem, x_label = get_x_axis(data_fem[-1, :])
        if show_dq:
            ax.plot(x_fem, data_fem[0, :], color='gray', linestyle='--', alpha=0.6, label=r'FEM $\Psi_d$')
            ax.plot(x_fem, data_fem[1, :], color='gray', linestyle=':', alpha=0.6, label=r'FEM $\Psi_q$')
        for i in phase_indices:
            color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
            ax.plot(x_fem, data_fem[2 + i, :], color=color, linestyle='--', alpha=0.3, label=f'FEM Phase {chr(65+i)}')

    if has_sf:
        data_sf = record.flux_linkage
        x_sf, x_label = get_x_axis(data_sf[-1, :])
        if show_dq:
            ax.plot(x_sf, data_sf[0, :], color='black', linestyle=s.linestyles[1], label=r'SF $\Psi_d$')
            ax.plot(x_sf, data_sf[1, :], color='black', linestyle=s.linestyles[0], label=r'SF $\Psi_q$')
        for i in phase_indices:
            color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
            ax.plot(x_sf, data_sf[2 + i, :], color=color, label=f'SF Phase {chr(65+i)}', linewidth=2.0)

    ax.set_xlabel(x_label, fontsize=s.label_size)
    ax.set_ylabel(r'Flux Linkage ($Wb$)', fontsize=s.label_size)
    ax.legend(frameon=True, loc='best', ncol=2)
    ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
    plt.tight_layout()
    plt.show()