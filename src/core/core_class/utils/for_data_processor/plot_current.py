import os
import paths
import numpy as np 
import matplotlib.pyplot as plt

def plot_current(data_processor, 
                 horizontal_axis = "mechanical_position", 
                 show_fem = True, 
                 plot = False,
                 figsize = None):
    root_dir = paths.configure_path()
    figure_dir = os.path.join(root_dir, "data", "repo", "figures")
    if not os.path.exists(figure_dir):
        os.makedirs(figure_dir)

    record = data_processor.motor.record
    n_phase = data_processor.motor.winding_data.phase
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    s = data_processor.plot_style

    if figsize is None:
        current_figsize = (16, 10)
    else:
        current_figsize = figsize

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
        
    fig = None
    if hasattr(record, "currents"):
        data = record.currents
        x_data, x_label = get_x_axis(data[-1, :])
        
        fig, ax = plt.subplots(figsize=current_figsize)
        
        ax.plot(x_data, data[0, :], color='black', linestyle=s.linestyles[1], 
                label=r'$I_d$', linewidth=1.5)
        ax.plot(x_data, data[1, :], color='black', linestyle=s.linestyles[0], 
                label=r'$I_q$', linewidth=1.5)
        
        for i in range(n_phase):
            color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
            ax.plot(x_data, data[2 + i, :], color=color, 
                    label=f'Phase {chr(65+i)}', linewidth=2.0)
            
        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Current ($A$)', fontsize=s.label_size, family=s.font_family)
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        ax.legend(frameon=True, loc='best', ncol=2, fontsize=s.legend_size)
        ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        
        plt.tight_layout()
        
        wave_path = os.path.join(figure_dir, "current.png")
        fig.savefig(wave_path, bbox_inches='tight', dpi=300)
        
        if plot:
            plt.show()
            
    return fig