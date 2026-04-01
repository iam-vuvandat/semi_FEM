import numpy as np 
import matplotlib.pyplot as plt

def plot_mechanical_power(data_processor, horizontal_axis = "mechanical_position"):
    record = data_processor.motor.record
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    
    # Chủ động đọc các thông số từ SimpleNamespace
    s = data_processor.plot_style

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
        
    if hasattr(record, "mechanical_power"):
        # data[0, :] là công suất (W), data[1, :] là vị trí (rad)
        data = record.mechanical_power
        p_values = data[0, :]
        x_data, x_label = get_x_axis(data[1, :])
        
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Vẽ công suất cơ học tức thời (Màu xanh lá đậm)
        ax.plot(x_data, p_values, color='forestgreen', linestyle=s.linestyles[0], 
                label='Mechanical Power', linewidth=2.5)
        
        # Vẽ công suất cơ học trung bình (Nét đứt đỏ)
        if hasattr(record, "average_mechanical_power"):
            avg_p = record.average_mechanical_power
            ax.axhline(y=avg_p, color='red', linestyle=s.linestyles[1], 
                       label=f'Avg: {avg_p:.2f} $W$', linewidth=1.5)
        
        # Chủ động thiết lập font chữ và cỡ chữ
        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Power ($W$)', fontsize=s.label_size, family=s.font_family)
        
        # Thiết lập cỡ chữ cho các con số trên trục
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        # Thiết lập cỡ chữ cho chú thích
        ax.legend(frameon=True, loc='best', fontsize=s.legend_size)
        
        # Chủ động thiết lập lưới theo style
        ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        
        if np.min(p_values) >= 0:
            ax.set_ylim(bottom=0, top=np.max(p_values) * 1.2)
            
        plt.tight_layout()
        plt.show()