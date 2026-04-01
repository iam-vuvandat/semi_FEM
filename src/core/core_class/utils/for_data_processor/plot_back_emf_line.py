import numpy as np 
import matplotlib.pyplot as plt

def plot_back_emf_line(data_processor, horizontal_axis = "mechanical_position"):
    record = data_processor.motor.record
    n_phase = data_processor.motor.winding_data.phase
    shaft_speed = (data_processor.motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    
    # Chủ động lấy các thông số từ SimpleNamespace
    s = data_processor.plot_style

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            return theta_data / shaft_speed, r'Time ($s$)'
        else:
            return theta_data, r'Rotor Position ($rad$)'
        
    if hasattr(record, "back_emf"):
        data_phase = record.back_emf
        x_data, x_label = get_x_axis(record.flux_linkage[-1, :])
        
        fig, ax = plt.subplots(figsize=(16, 10))
        
        for i in range(n_phase):
            # V_ab = V_a - V_b
            v_line = data_phase[i, :] - data_phase[(i + 1) % n_phase, :]
            
            color = s.phase_colors[i % 3] if n_phase == 3 else s.colors[i % len(s.colors)]
            label_name = f'{chr(65+i)}{chr(65+(i+1)%n_phase)}'
            
            ax.plot(x_data, v_line, color=color, linestyle=s.linestyles[0], 
                    label=f'Line {label_name}', linewidth=2.0)
            
        # Chủ động áp dụng font chữ và cỡ chữ
        ax.set_xlabel(x_label, fontsize=s.label_size, family=s.font_family)
        ax.set_ylabel(r'Line Back EMF ($V$)', fontsize=s.label_size, family=s.font_family)
        
        # Thiết lập cỡ chữ cho các con số trên trục
        ax.tick_params(axis='both', which='major', labelsize=s.tick_size)
        
        # Thiết lập cỡ chữ cho chú thích
        ax.legend(frameon=True, loc='best', ncol=2 if n_phase > 3 else 1, fontsize=s.legend_size)
        
        # Chủ động thiết lập lưới theo style
        ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
        
        plt.tight_layout()
        plt.show()