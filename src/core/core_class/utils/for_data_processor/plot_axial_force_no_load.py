import os
import paths
import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.decompose_harmonics import decompose_harmonics

def plot_axial_force_no_load(data_processor, 
                             horizontal_axis = "mechanical_position", 
                             show_fem = True, 
                             plot = False, 
                             revert = True):
    
    root_dir = paths.configure_path()
    figure_dir = os.path.join(root_dir, "data", "repo", "figures")
    if not os.path.exists(figure_dir):
        os.makedirs(figure_dir)

    motor = data_processor.motor
    record = motor.record
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    s = data_processor.plot_style
    fem_mult = -1 if revert else 1
    max_h = 15

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
    
    has_mrn = hasattr(record, "axial_force_no_load") and record.axial_force_no_load is not None
    has_fem = hasattr(record, "axial_force_no_load_fem") and record.axial_force_no_load_fem is not None and show_fem

    if not has_mrn and not has_fem:
        print("\033[93mWarning: No no-load axial force data found.\033[0m")
        return None

    fig_wave = plt.figure(figsize=(fig_width, fig_height))
    ax = plt.gca()
    
    x_label = ""
    color_fem = '#7F7F7F'  
    color_mrn = '#B22222'  

    all_y_values = []

    if has_fem:
        data_fem = record.axial_force_no_load_fem
        x_fem, x_label = get_x_axis(data_fem[-1, :])
        val_fem = data_fem[0, :] * fem_mult
        all_y_values.extend(val_fem)
        
        average_fem = np.mean(val_fem)
        label_fem = r'Axial Force (FEM, $F_{avg}$ = ' + f'{average_fem:.2f} N)'
        
        ax.plot(x_fem, val_fem, color=color_fem, linestyle='-', linewidth=1.5, 
                label=label_fem)
        
        amps_fem, _ = decompose_harmonics(val_fem, n_harmonics=max_h)
        h_orders = np.arange(len(amps_fem))
        record.axial_force_no_load_harmonic_fem = np.vstack((amps_fem, h_orders))

    if has_mrn:
        data_mrn = record.axial_force_no_load
        x_mrn, x_label = get_x_axis(data_mrn[-1, :])
        val_mrn = data_mrn[0, :]
        all_y_values.extend(val_mrn)
        
        average_mrn = np.mean(val_mrn)
        label_mrn = r'Axial Force (MRN, $F_{avg}$ = ' + f'{average_mrn:.2f} N)'
        
        ax.plot(x_mrn, val_mrn, color=color_mrn, linestyle='-', linewidth=3.0, 
                label=label_mrn)
        
        amps_mrn, _ = decompose_harmonics(val_mrn, n_harmonics=max_h)
        h_orders = np.arange(len(amps_mrn))
        record.axial_force_no_load_harmonic = np.vstack((amps_mrn, h_orders))

    ax.set_xlabel(x_label, fontsize=s.label_size)
    ax.set_ylabel('Axial Force (N)', fontsize=s.label_size)
    ax.legend(frameon=True, loc='best', fontsize=s.legend_size)
    ax.grid(True, which='major', linestyle='-', linewidth=s.grid_linewidth)
    ax.margins(x=0)
    
    if all_y_values:
        y_min = np.min(all_y_values)
        y_max = np.max(all_y_values)
        y_range = y_max - y_min
        if y_range == 0:
            y_range = 1.0
            
        padding = 0.15 * y_range
        ax.set_ylim(y_min - padding, y_max + padding)
    
    plt.tight_layout()
    
    wave_path = os.path.join(figure_dir, "axial_force_no_load.png")
    fig_wave.savefig(wave_path, bbox_inches='tight', dpi=300)
    
    if plot:
        plt.show()
        
    return fig_wave