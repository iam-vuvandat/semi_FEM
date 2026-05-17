import numpy as np 
import matplotlib.pyplot as plt

def plot_airgap_flux_density(data_processor, 
                             horizontal_axis="mechanical_position", 
                             show_fem=True, 
                             plot=False):
    
    if not plot:
        return
        
    motor = data_processor.motor
    record = motor.record
    shaft_speed = (motor.mechanical_data.shaft_speed * np.pi * 2) / 60 
    s = data_processor.plot_style

    # Tỉ lệ vàng (Golden Ratio 1.618:1)
    fig_width = 14
    fig_height = fig_width / 1.618

    def get_x_axis(theta_data):
        if horizontal_axis == "time":
            # Cảnh báo: Với Airgap Flux Density, dữ liệu là phân bố không gian (snapshot tại 1 thời điểm).
            # Quy đổi ra time ở đây mang ý nghĩa mapping góc không gian tương đương với trục thời gian quay.
            return theta_data / shaft_speed, r'Time Equivalent ($s$)'
        else:
            return theta_data, r'Angular Position ($rad$)'
    
    has_mrn = hasattr(record, "airgap_flux_density")
    has_fem = hasattr(record, "airgap_flux_density_fem") and show_fem

    plt.figure(figsize=(fig_width, fig_height))
    ax = plt.gca()
    x_label = ""

    # Vẽ FEM trước (Làm nền): Nét đứt (linestyle='--'), mảnh (linewidth=1.2)
    if has_fem:
        data_fem = record.airgap_flux_density_fem
        x_fem, x_label = get_x_axis(data_fem[4, :])
        
        ax.plot(x_fem, data_fem[0, :], color='green', linestyle='--', linewidth=1.2, label=r'$B_r$ (FEM)')
        ax.plot(x_fem, data_fem[1, :], color='orange', linestyle='--', linewidth=1.2, label=r'$B_t$ (FEM)')
        ax.plot(x_fem, data_fem[2, :], color='blue', linestyle='--', linewidth=1.2, label=r'$B_z$ (FEM)')

    # Vẽ MRN sau (Nằm đè lên): Nét liền (linestyle='-'), đậm (linewidth=3.0)
    if has_mrn:
        data_mrn = record.airgap_flux_density
        x_mrn, x_label = get_x_axis(data_mrn[4, :])
        
        ax.plot(x_mrn, data_mrn[0, :], color='green', linestyle='-', linewidth=3.0, label=r'$B_r$ (MRN)')
        ax.plot(x_mrn, data_mrn[1, :], color='orange', linestyle='-', linewidth=3.0, label=r'$B_t$ (MRN)')
        ax.plot(x_mrn, data_mrn[2, :], color='blue', linestyle='-', linewidth=3.0, label=r'$B_z$ (MRN)')

    ax.set_xlabel(x_label, fontsize=s.label_size)
    ax.set_ylabel('Airgap Flux Density (T)', fontsize=s.label_size)
    
    # Đặt legend ở góc ngoài hoặc góc trống để không đè lên dải sóng từ thông
    ax.legend(frameon=True, loc='upper right', fontsize=s.legend_size, ncol=2)
    ax.grid(True, which='both', linestyle='-', linewidth=s.grid_linewidth)
    
    plt.tight_layout()
    plt.show()