import numpy as np 
import matplotlib.pyplot as plt

def plot_mechanical_power(data_processor, 
                          horizontal_axis = "mechanical_position", 
                          show_fem = True, 
                          plot = False, 
                          revert = True):
    
    motor = data_processor.motor
    record = motor.record
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    s = data_processor.plot_style
    fem_mult = -1 if revert else 1

    # Tỉ lệ vàng (Golden Ratio 1.618:1)
    fig_width = 14
    fig_height = fig_width / 1.618

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
    
    has_mrn = hasattr(record, "mechanical_power")
    has_fem = hasattr(record, "mechanical_power_fem") and show_fem

    fig_wave = plt.figure(figsize=(fig_width, fig_height))
    ax = plt.gca()
    x_label = ""

    # Vẽ FEM trước: Màu đen, mảnh (linewidth=1.0), nét liền
    if has_fem:
        data_fem = record.mechanical_power_fem
        x_fem, x_label = get_x_axis(data_fem[-1, :])
        val_fem = data_fem[0, :] * fem_mult
        ax.plot(x_fem, val_fem, color='black', linestyle='-', linewidth=1.0, 
                label='Mechanical Power (FEM)')

    # Vẽ MRN sau để nằm đè lên: Màu đỏ, đậm (linewidth=3.5), nét liền
    if has_mrn:
        data_mrn = record.mechanical_power
        x_mrn, x_label = get_x_axis(data_mrn[-1, :])
        val_mrn = data_mrn[0, :]
        ax.plot(x_mrn, val_mrn, color='red', linestyle='-', linewidth=3.5, 
                label='Mechanical Power (MRN)')
        
        # Đường trung bình (nếu có) theo phong cách MRN
        if hasattr(record, "average_mechanical_power"):
            ax.axhline(y=record.average_mechanical_power, color='red', linestyle='--')

    ax.set_xlabel(x_label, fontsize=s.label_size)
    ax.set_ylabel('Power (W)', fontsize=s.label_size)
    ax.legend(frameon=True, loc='lower right', fontsize=s.legend_size)
    ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
    
    plt.tight_layout()
    
    if plot:
        plt.show()
        
    return fig_wave