import numpy as np 
import matplotlib.pyplot as plt

def plot_cogging_torque(data_processor, horizontal_axis = "mechanical_position", 
                        show_fem = True, plot = False, revert = True):
    
    if not plot:
        return
        
    motor = data_processor.motor
    if not hasattr(motor, "record"):
        return

    record = motor.record
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    s = data_processor.plot_style

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
        
    has_sf = hasattr(record, "cogging")
    has_fem = hasattr(record, "cogging_fem") and show_fem

    if not has_sf and not has_fem:
        print("\033[93mWarning: No cogging torque data found in record.\033[0m")
        return

    fig, ax = plt.subplots(figsize=(16, 10))
    x_label = ""
    fem_mult = -1 if revert else 1

    if has_fem:
        data_fem = record.cogging_fem
        x_fem, x_label = get_x_axis(data_fem[1, :])
        cogging_fem_val = data_fem[0, :] * fem_mult
        ax.plot(x_fem, cogging_fem_val, color='gray', linestyle='--', alpha=0.6, 
                linewidth=1.5, label='FEM Cogging Torque')

    if has_sf:
        data_sf = record.cogging
        x_sf, x_label = get_x_axis(data_sf[1, :])
        cogging_sf_val = data_sf[0, :] # Giữ nguyên dấu MBGRN
        ax.plot(x_sf, cogging_sf_val, color='brown', linestyle='-', 
                linewidth=2.5, label='SF Cogging Torque')

    ax.axhline(y=0, color='black', linestyle=':', linewidth=1.0)
    ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
    ax.set_ylabel(r'Cogging Torque ($N.m$)', fontsize=s.label_size, family=s.font_family)
    ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
    ax.legend(frameon=True, loc='best', fontsize=s.legend_size, ncol=2)
    ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
    
    all_vals = []
    if has_sf: all_vals.extend(cogging_sf_val)
    if has_fem: all_vals.extend(cogging_fem_val)
    
    if all_vals:
        limit = np.max(np.abs(all_vals)) * 1.5
        if limit > 0:
            ax.set_ylim(-limit, limit)
            
    plt.tight_layout()
    plt.show()