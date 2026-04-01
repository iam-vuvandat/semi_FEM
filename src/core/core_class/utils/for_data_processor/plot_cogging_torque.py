import numpy as np 
import matplotlib.pyplot as plt

def plot_cogging_torque(data_processor, horizontal_axis = "mechanical_position"):
    record = data_processor.motor.record
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    
    # Chủ động đọc các thông số từ SimpleNamespace
    s = data_processor.plot_style

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
        
    if hasattr(record, "cogging"):
        data = record.cogging
        # data[0, :] là giá trị mô-men, hàng cuối cùng là vị trí rotor
        x_data, x_label = get_x_axis(data[-1, :])
        cogging_torque = data[0, :]
        
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Vẽ mô-men răng
        ax.plot(x_data, cogging_torque, color='brown', linestyle=s.linestyles[0], 
                label='Cogging Torque', linewidth=2.5)
        
        # Đường zero tham chiếu
        ax.axhline(y=0, color='black', linestyle=s.linestyles[1], linewidth=1.0)
        
        # Chủ động thiết lập font chữ và cỡ chữ cho nhãn trục
        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Cogging Torque ($N.m$)', fontsize=s.label_size, family=s.font_family)
        
        # Thiết lập cỡ chữ cho các con số trên trục (ticks)
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        # Thiết lập cỡ chữ cho chú thích (legend)
        ax.legend(frameon=True, loc='best', fontsize=s.legend_size)
        
        # Chủ động thiết lập lưới theo style
        ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        
        # Tự động cân đối trục Y quanh giá trị 0
        limit = np.max(np.abs(cogging_torque)) * 1.5
        if limit > 0:
            ax.set_ylim(-limit, limit)
            
        plt.tight_layout()
        plt.show()