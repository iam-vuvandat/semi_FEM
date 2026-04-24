import numpy as np 
import matplotlib.pyplot as plt

def plot_mechanical_power(data_processor, horizontal_axis = "mechanical_position", 
                          show_fem = True, plot = False, revert = True):
    
    if not plot:
        return
        
    motor = data_processor.motor
    record = motor.record
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    s = data_processor.plot_style
    fem_mult = -1 if revert else 1

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
    
    has_sf = hasattr(record, "mechanical_power")
    has_fem = hasattr(record, "mechanical_power_fem") and show_fem

    fig, ax = plt.subplots(figsize=(16, 10))
    x_label = ""

    if has_fem:
        data_fem = record.mechanical_power_fem
        x_fem, x_label = get_x_axis(data_fem[-1, :])
        val_fem = data_fem[0, :] * fem_mult
        ax.plot(x_fem, val_fem, color='gray', linestyle='--', alpha=0.6, label='FEM Power')

    if has_sf:
        data_sf = record.mechanical_power
        x_sf, x_label = get_x_axis(data_sf[-1, :])
        val_sf = data_sf[0, :]
        ax.plot(x_sf, val_sf, color='forestgreen', label='SF Power', linewidth=2.5)
        if hasattr(record, "average_mechanical_power"):
            ax.axhline(y=record.average_mechanical_power, color='red', linestyle='--')

    ax.set_xlabel(x_label, fontsize=s.label_size)
    ax.set_ylabel(r'Power ($W$)', fontsize=s.label_size)
    ax.legend(frameon=True, loc='best', ncol=2)
    ax.grid(True, linestyle='-', linewidth=s.grid_linewidth)
    plt.tight_layout()
    plt.show()