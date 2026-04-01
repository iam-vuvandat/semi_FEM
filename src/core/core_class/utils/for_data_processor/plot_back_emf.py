import numpy as np 
import matplotlib.pyplot as plt

def plot_back_emf(data_processor, horizontal_axis = "mechanical_position"):
    record = data_processor.motor.record
    n_phase = data_processor.motor.winding_data.phase
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    
    # Chủ động đọc các thông số từ SimpleNamespace
    s = data_processor.plot_style

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
        
    if hasattr(record, "back_emf"):
        data = record.back_emf
        # Lấy trục theta từ flux_linkage để đảm bảo tính đồng bộ thời điểm
        x_data, x_label = get_x_axis(record.flux_linkage[-1, :])
        
        fig, ax = plt.subplots(figsize=(16, 10))
        
        for i in range(n_phase):
            color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
            ax.plot(x_data, data[i, :], color=color, linestyle=s.linestyles[0], 
                    label=f'Phase {chr(65+i)}', linewidth=2.0)
            
        # Chủ động thiết lập font chữ và cỡ chữ
        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Back EMF ($V$)', fontsize=s.label_size, family=s.font_family)
        
        # Thiết lập cỡ chữ cho các con số trên trục
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        # Thiết lập cỡ chữ cho chú thích
        ax.legend(frameon=True, loc='best', ncol=2 if n_phase > 3 else 1, fontsize=s.legend_size)
        
        # Chủ động thiết lập lưới
        ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        
        plt.tight_layout()
        plt.show()