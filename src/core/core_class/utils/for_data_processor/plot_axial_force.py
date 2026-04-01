import numpy as np 
import matplotlib.pyplot as plt

def plot_axial_force(data_processor, horizontal_axis = "mechanical_position"):
    record = data_processor.motor.record
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    
    # Chủ động đọc các thông số từ plot_style (SimpleNamespace)
    s = data_processor.plot_style
    
    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
        
    if hasattr(record, "mst_data"):
        data = record.mst_data
        x_data, x_label = get_x_axis(data[-1, :])
        
        # Lực dọc trục nằm ở chỉ số 2 (Trục Z)
        force_z = data[2, :]
        avg_force = np.mean(force_z)
        
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Vẽ lực dọc trục tức thời
        ax.plot(x_data, force_z, color='#AA3377', linestyle=s.linestyles[0], 
                label='Axial Force', linewidth=3.0)
        
        # Vẽ lực trung bình
        ax.axhline(y=avg_force, color='black', linestyle=s.linestyles[1], 
                   label=f'Avg: {avg_force:.2f} $N$', linewidth=1.5)
        
        # Chủ động thiết lập font chữ cho các thành phần đồ thị
        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Axial Force ($N$)', fontsize=s.label_size, family=s.font_family)
        
        # Thiết lập cỡ chữ cho các con số trên trục (ticks)
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        # Thiết lập cỡ chữ cho chú thích (legend)
        ax.legend(frameon=True, loc='best', fontsize=s.legend_size)
        
        # Chủ động thiết lập lưới
        ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        
        # Thường lực dọc trục trong AFPM rất lớn và luôn dương (lực hút)
        if np.min(force_z) > 0:
            ax.set_ylim(bottom=0, top=np.max(force_z) * 1.2)
            
        plt.tight_layout()
        plt.show()