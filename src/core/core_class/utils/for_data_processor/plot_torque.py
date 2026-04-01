import numpy as np 
import matplotlib.pyplot as plt

def plot_torque(data_processor, horizontal_axis = "mechanical_position"):
    record = data_processor.motor.record
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    
    # Chủ động đọc các thông số từ SimpleNamespace
    s = data_processor.plot_style

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
        
    if hasattr(record, "mst_data"):
        data = record.mst_data
        # data[3, :] là mô-men xoắn, hàng cuối cùng là vị trí rotor
        x_data, x_label = get_x_axis(data[-1, :])
        torque_z = data[3, :]
        avg_torque = np.mean(torque_z)
        
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Vẽ mô-men tức thời (Sử dụng màu cam đậm s.colors[8] cho tương phản)
        ax.plot(x_data, torque_z, color=s.colors[8], linestyle=s.linestyles[0], 
                label='Electromagnetic Torque', linewidth=3.0)
        
        # Vẽ đường mô-men trung bình (Nét đứt đen)
        ax.axhline(y=avg_torque, color='black', linestyle=s.linestyles[1], 
                   label=f'Avg: {avg_torque:.2f} $N.m$', linewidth=1.5)
        
        # Chủ động thiết lập font chữ và cỡ chữ từ plot_style
        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Torque ($N.m$)', fontsize=s.label_size, family=s.font_family)
        
        # Thiết lập cỡ chữ cho các con số trên trục (ticks)
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        # Thiết lập cỡ chữ cho chú thích (legend)
        ax.legend(frameon=True, loc='best', fontsize=s.legend_size)
        
        # Chủ động thiết lập lưới
        ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        
        # Tự động điều chỉnh trục y để quan sát Torque Ripple rõ hơn
        if np.min(torque_z) > 0:
            ax.set_ylim(bottom=0, top=np.max(torque_z) * 1.2)
            
        plt.tight_layout()
        plt.show()