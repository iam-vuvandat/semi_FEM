import numpy as np 
import matplotlib.pyplot as plt

def plot_torque(data_processor, 
                horizontal_axis = "mechanical_position", 
                show_fem = True, 
                plot = False, 
                revert = True):
    
    motor = data_processor.motor
    record = motor.record
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    s = data_processor.plot_style

    # Tỉ lệ vàng (Golden Ratio 1.618:1)
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
    
    has_mrn = hasattr(record, "torque")
    has_fem = hasattr(record, "torque_fem") and show_fem
    fem_mult = -1 if revert else 1

    fig_wave = plt.figure(figsize=(fig_width, fig_height))
    ax = plt.gca()
    x_label = ""

    # Cấu hình bộ màu: Đỏ đô trầm và Xám học thuật dịu
    color_fem = '#7F7F7F'  # Màu xám dịu (Muted Gray)
    color_mrn = '#B22222'  # Đỏ đô trầm (Firebrick Red)

    # Khởi tạo mảng lưu giá trị để tính giới hạn trục Y
    all_y_values = []

    # Vẽ FEM trước: Nét liền, mảnh
    if has_fem:
        data_fem = record.torque_fem
        x_fem, x_label = get_x_axis(data_fem[-1, :])
        val_fem = data_fem[0, :] * fem_mult
        all_y_values.extend(val_fem)
        
        avg_fem = np.mean(val_fem)
        label_fem = r'Torque (FEM, $T_{avg}$ = ' + f'{avg_fem:.2f} Nm)'
        
        ax.plot(x_fem, val_fem, color=color_fem, linestyle='-', linewidth=1.5, 
                label=label_fem)

    # Vẽ MBGRN sau đè lên: Nét liền, đậm, không dùng marker
    if has_mrn:
        data_mrn = record.torque
        x_mrn, x_label = get_x_axis(data_mrn[-1, :])
        val_mrn = data_mrn[0, :]
        all_y_values.extend(val_mrn)
        
        avg_mrn = np.mean(val_mrn)
        label_mrn = r'Torque (MBGRN, $T_{avg}$ = ' + f'{avg_mrn:.2f} Nm)'
        
        ax.plot(x_mrn, val_mrn, color=color_mrn, linestyle='-', linewidth=3.0, 
                label=label_mrn)

    # Tự động tính toán giới hạn trục Y để chừa khoảng trống lề trên và lề dưới
    if all_y_values:
        y_min = np.min(all_y_values)
        y_max = np.max(all_y_values)
        y_range = y_max - y_min
        if y_range == 0:
            y_range = 1.0  # Tránh lỗi chia cho 0 nếu đồ thị là đường thẳng tuyệt đối
            
        # Chừa ra biên độ 15% dải dữ liệu cho lề trên và lề dưới
        padding = 0.15 * y_range
        ax.set_ylim(y_min - padding, y_max + padding)

    ax.set_xlabel(x_label, fontsize=s.label_size)
    ax.set_ylabel('Torque (Nm)', fontsize=s.label_size)
    
    ax.legend(frameon=True, loc='best', fontsize=s.legend_size)
    ax.grid(True, which='major', linestyle='-', linewidth=s.grid_linewidth)
    ax.margins(x=0)
    
    plt.tight_layout()
    
    if plot:
        plt.show()
        
    return fig_wave