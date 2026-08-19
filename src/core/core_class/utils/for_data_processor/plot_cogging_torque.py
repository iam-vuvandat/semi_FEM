import os
import paths
import numpy as np 
import matplotlib.pyplot as plt
from src.core.solver.utils.duplicate_data import duplicate_data
from src.core.solver.utils.decompose_harmonics import decompose_harmonics

def plot_cogging_torque(data_processor, 
                        horizontal_axis = "mechanical_position", 
                        show_fem = True, 
                        plot = False, 
                        revert = True,
                        num_periods = 1,
                        figsize = None):
    
    root_dir = paths.configure_path()
    figure_dir = os.path.join(root_dir, "data", "repo", "figures")
    if not os.path.exists(figure_dir):
        os.makedirs(figure_dir)

    motor = data_processor.motor
    if not hasattr(motor, "record"):
        return None

    record = motor.record
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60
    s = data_processor.plot_style
    fem_mult = -1 if revert else 1
    max_h = 15

    if figsize is None:
        fig_width = 14
        fig_height = fig_width / 1.618
        current_figsize = (fig_width, fig_height)
    else:
        current_figsize = figsize

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
        
    has_mrn = hasattr(record, "cogging") and record.cogging is not None
    has_fem = hasattr(record, "cogging_fem") and record.cogging_fem is not None and show_fem

    if not has_mrn and not has_fem:
        print("\033[93mWarning: No cogging torque data found in record.\033[0m")
        return None

    fig_wave = plt.figure(figsize=current_figsize)
    ax = plt.gca()
    x_label = ""

    color_fem = '#7F7F7F'  
    color_mrn = '#B22222'  

    all_y_values = []

    if has_fem:
        base_fem = record.cogging_fem
        base_val_fem = base_fem[0, :] * fem_mult
        amps_fem, _ = decompose_harmonics(base_val_fem, n_harmonics=max_h)
        h_orders = np.arange(len(amps_fem))
        record.cogging_harmonic_fem = np.vstack((amps_fem, h_orders))

        data_fem = base_fem
        if num_periods > 1:
            data_fem = duplicate_data(data_fem, half_open_interval=True, num_periods=num_periods).duplicated_data
            
        x_fem, x_label = get_x_axis(data_fem[1, :])
        cogging_fem_val = data_fem[0, :] * fem_mult
        all_y_values.extend(cogging_fem_val)
        
        peak_fem = np.max(np.abs(cogging_fem_val))
        label_fem = r'Cogging Torque (FEM, $|T_{max}|$ = ' + f'{peak_fem:.2f} Nm)'
        
        ax.plot(x_fem, cogging_fem_val, color=color_fem, linestyle='-', linewidth=1.5, label=label_fem)

    if has_mrn:
        base_mrn = record.cogging
        base_val_mrn = base_mrn[0, :]
        amps_mrn, _ = decompose_harmonics(base_val_mrn, n_harmonics=max_h)
        h_orders = np.arange(len(amps_mrn))
        record.cogging_harmonic = np.vstack((amps_mrn, h_orders))

        data_mrn = base_mrn
        if num_periods > 1:
            data_mrn = duplicate_data(data_mrn, half_open_interval=True, num_periods=num_periods).duplicated_data
            
        x_mrn, x_label = get_x_axis(data_mrn[1, :])
        cogging_mrn_val = data_mrn[0, :]
        all_y_values.extend(cogging_mrn_val)
        
        peak_mrn = np.max(np.abs(cogging_mrn_val))
        label_mrn = r'Cogging Torque (MBGRN, $|T_{max}|$ = ' + f'{peak_mrn:.2f} Nm)'
        
        ax.plot(x_mrn, cogging_mrn_val, color=color_mrn, linestyle='-', linewidth=3.0, label=label_mrn)

    ax.axhline(y=0, color='black', linestyle=':', linewidth=1.0)
    ax.set_xlabel(x_label, fontsize=s.label_size)
    ax.set_ylabel('Cogging Torque (Nm)', fontsize=s.label_size)
    
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
    
    wave_path = os.path.join(figure_dir, "cogging_torque.png")
    fig_wave.savefig(wave_path, bbox_inches='tight', dpi=300)
    
    if plot:
        plt.show()
        
    return fig_wave