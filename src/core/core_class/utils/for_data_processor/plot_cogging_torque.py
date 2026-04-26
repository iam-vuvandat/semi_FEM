import numpy as np 
import matplotlib.pyplot as plt

def plot_cogging_torque(data_processor, 
                        horizontal_axis = "mechanical_position", 
                        show_fem = True, 
                        plot = False, 
                        revert = True):
    
    if not plot:
        return
        
    motor = data_processor.motor
    if not hasattr(motor, "record"):
        return

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
        
    has_mrn = hasattr(record, "cogging")
    has_fem = hasattr(record, "cogging_fem") and show_fem

    if not has_mrn and not has_fem:
        print("\033[93mWarning: No cogging torque data found in record.\033[0m")
        return

    plt.figure(figsize=(fig_width, fig_height))
    ax = plt.gca()
    x_label = ""

    # Vẽ FEM trước: Màu đen, mảnh (linewidth=1.0), nét liền
    if has_fem:
        data_fem = record.cogging_fem
        x_fem, x_label = get_x_axis(data_fem[1, :])
        cogging_fem_val = data_fem[0, :] * fem_mult
        ax.plot(x_fem, cogging_fem_val, color='black', linestyle='-', 
                linewidth=1.0, label='Cogging Torque (FEM)')

    # Vẽ MRN sau để nằm đè lên: Màu đỏ, đậm (linewidth=3.5), nét liền
    if has_mrn:
        data_mrn = record.cogging
        x_mrn, x_label = get_x_axis(data_mrn[1, :])
        cogging_mrn_val = data_mrn[0, :]
        ax.plot(x_mrn, cogging_mrn_val, color='red', linestyle='-', 
                linewidth=3.5, label='Cogging Torque (MRN)')

    # Định dạng đồ thị
    ax.axhline(y=0, color='black', linestyle=':', linewidth=1.0)
    ax.set_xlabel(x_label, fontsize=s.label_size)
    ax.set_ylabel('Cogging Torque (Nm)', fontsize=s.label_size)
    ax.legend(frameon=True, loc='best', fontsize=s.legend_size, ncol=2)
    ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
    
    # Thiết lập giới hạn trục Y đối xứng
    all_vals = []
    if has_mrn: all_vals.extend(cogging_mrn_val)
    if has_fem: all_vals.extend(cogging_fem_val)
    
    if all_vals:
        limit = np.max(np.abs(all_vals)) * 1.5
        if limit > 0:
            ax.set_ylim(-limit, limit)
            
    plt.tight_layout()
    plt.show()