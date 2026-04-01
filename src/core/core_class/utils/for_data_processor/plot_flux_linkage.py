import numpy as np 
import matplotlib.pyplot as plt

def plot_flux_linkage(data_processor, horizontal_axis = "mechanical_position"):
    record = data_processor.motor.record
    n_phase = data_processor.motor.winding_data.phase
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    
    # Chủ động đọc thông tin từ SimpleNamespace
    s = data_processor.plot_style

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
        
    if hasattr(record, "flux_linkage"):
        data = record.flux_linkage
        # Hàng cuối cùng của mảng flux_linkage chứa dữ liệu vị trí rotor (theta)
        x_data, x_label = get_x_axis(data[-1, :])
        
        fig, ax = plt.subplots(figsize=(16, 10))
        
        # Vẽ các thành phần d-q
        ax.plot(x_data, data[0, :], color='black', linestyle=s.linestyles[1], 
                label=r'$\Psi_d$', linewidth=1.5)
        ax.plot(x_data, data[1, :], color='black', linestyle=s.linestyles[0], 
                label=r'$\Psi_q$', linewidth=1.5)
        
        # Vẽ các thành phần pha
        for i in range(n_phase):
            color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
            ax.plot(x_data, data[2 + i, :], color=color, 
                    label=f'Phase {chr(65+i)}', linewidth=2.0)
            
        # Chủ động thiết lập font chữ và cỡ chữ từ plot_style
        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Flux Linkage ($Wb$)', fontsize=s.label_size, family=s.font_family)
        
        # Thiết lập cỡ chữ cho các ticks
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        # Thiết lập cỡ chữ cho chú thích (legend)
        ax.legend(frameon=True, loc='best', ncol=2, fontsize=s.legend_size)
        
        # Chủ động thiết lập lưới
        ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        
        plt.tight_layout()
        plt.show()