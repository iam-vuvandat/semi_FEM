import numpy as np 
import matplotlib.pyplot as plt

def plot_airgap_flux_density_no_load(data_processor, 
                                     horizontal_axis="mechanical_position", 
                                     show_fem=True, 
                                     plot=False):
    
    if not plot:
        return
        
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

    plt.figure(figsize=(fig_width, fig_height))
    ax = plt.gca()
    x_label = ""

    if has_fem:
        data_fem = record.airgap_flux_density_no_load_fem
        x_fem, x_label = get_x_axis(data_fem[4, :])
        
        ax.plot(x_fem, data_fem[0, :], color='green', linestyle='--', linewidth=1.2, label=r'$B_r$ (FEM No-Load)')
        ax.plot(x_fem, data_fem[1, :], color='orange', linestyle='--', linewidth=1.2, label=r'$B_t$ (FEM No-Load)')
        ax.plot(x_fem, data_fem[2, :], color='blue', linestyle='--', linewidth=1.2, label=r'$B_z$ (FEM No-Load)')

    if has_mrn:
        data_mrn = record.airgap_flux_density_no_load
        x_mrn, x_label = get_x_axis(data_mrn[4, :])
        
        ax.plot(x_mrn, data_mrn[0, :], color='green', linestyle='-', linewidth=3.0, label=r'$B_r$ (MRN No-Load)')
        ax.plot(x_mrn, data_mrn[1, :], color='orange', linestyle='-', linewidth=3.0, label=r'$B_t$ (MRN No-Load)')
        ax.plot(x_mrn, data_mrn[2, :], color='blue', linestyle='-', linewidth=3.0, label=r'$B_z$ (MRN No-Load)')

    ax.set_xlabel(x_label, fontsize=s.label_size)
    ax.set_ylabel('Airgap Flux Density No-Load (T)', fontsize=s.label_size)
    
    ax.legend(frameon=True, loc='upper right', fontsize=s.legend_size, ncol=2)
    ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
    
    plt.tight_layout()
    plt.show()