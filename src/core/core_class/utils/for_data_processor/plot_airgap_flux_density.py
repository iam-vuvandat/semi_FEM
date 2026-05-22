import numpy as np 
import matplotlib.pyplot as plt

def plot_airgap_flux_density(data_processor, 
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
    
    has_mrn = hasattr(record, "airgap_flux_density")
    has_fem = hasattr(record, "airgap_flux_density_fem") and show_fem

    plt.figure(figsize=(fig_width, fig_height))
    ax = plt.gca()
    x_label = ""

    # Định nghĩa bộ màu nghiêm túc (Muted Classic)
    color_r = '#B22222'  # Firebrick Red
    color_t = '#1F4E79'  # Navy Blue
    color_z = '#595959'  # Dim Gray

    if has_fem:
        data_fem = record.airgap_flux_density_fem
        x_fem, x_label = get_x_axis(data_fem[4, :])
        
        ax.plot(x_fem, data_fem[0, :], color=color_r, linestyle='-', linewidth=1.2, label=r'$B_r$ (FEM)')
        ax.plot(x_fem, data_fem[1, :], color=color_t, linestyle='-', linewidth=1.2, label=r'$B_t$ (FEM)')
        ax.plot(x_fem, data_fem[2, :], color=color_z, linestyle='-', linewidth=1.2, label=r'$B_z$ (FEM)')

    if has_mrn:
        data_mrn = record.airgap_flux_density
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
    plt.show()