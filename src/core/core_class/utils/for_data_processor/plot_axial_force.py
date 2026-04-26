import numpy as np 
import matplotlib.pyplot as plt

def plot_axial_force(data_processor, 
                     horizontal_axis = "mechanical_position", 
                     show_fem = True, 
                     plot = False, 
                     revert = True):
    
    if not plot:
        return
        
    motor = data_processor.motor
    record = motor.record
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    s = data_processor.plot_style
    fem_mult = -1 if revert else 1

    fig_width = 14
    fig_height = fig_width / 1.618

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
    
    has_mrn = hasattr(record, "axial_force")
    has_fem = hasattr(record, "axial_force_fem") and show_fem

    if not has_mrn and not has_fem:
        print("\033[93mWarning: No axial force data found.\033[0m")
        return

    plt.figure(figsize=(fig_width, fig_height))
    ax = plt.gca()
    
    val_mrn, val_fem = None, None
    x_label = ""

    if has_fem:
        data_fem = record.axial_force_fem
        x_fem, x_label = get_x_axis(data_fem[-1, :])
        val_fem = data_fem[0, :] * fem_mult
        average_fem = np.mean(val_fem)
        
        ax.plot(x_fem, val_fem, color='black', linestyle='-', linewidth=1.0, 
                label='Axial Force (FEM)')
        ax.axhline(y=average_fem, color='black', linestyle=':', alpha=0.5, 
                   label=f'Average Axial Force (FEM): {average_fem:.2f} N')

    if has_mrn:
        data_mrn = record.axial_force
        x_mrn, x_label = get_x_axis(data_mrn[-1, :])
        val_mrn = data_mrn[0, :]
        average_mrn = np.mean(val_mrn)
        
        ax.plot(x_mrn, val_mrn, color='red', linestyle='-', linewidth=3.5, 
                label='Axial Force (MRN)')
        ax.axhline(y=average_mrn, color='red', linestyle='--', alpha=0.8, 
                   label=f'Average Axial Force (MRN): {average_mrn:.2f} N')

    all_active_vals = []
    if val_mrn is not None: all_active_vals.extend(val_mrn)
    if val_fem is not None: all_active_vals.extend(val_fem)
    
    if all_active_vals:
        overall_average = np.mean(all_active_vals)
        max_deviation = np.max(np.abs(np.array(all_active_vals) - overall_average))
        padding = max_deviation * 1.5 if max_deviation > 0 else 10.0
        ax.set_ylim(overall_average - padding, overall_average + padding)

    ax.set_xlabel(x_label, fontsize=s.label_size)
    ax.set_ylabel('Axial Force (N)', fontsize=s.label_size)
    ax.legend(frameon=True, loc='best', fontsize=s.legend_size, ncol=2)
    ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
    
    plt.tight_layout()
    plt.show()