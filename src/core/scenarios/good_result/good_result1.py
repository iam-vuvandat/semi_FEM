import paths
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import math
pi = math.pi

re_create_motor = False
re_solve        = True
plot            = True
show_reluctance = True
filename        = "motor_ngon_1"

if not re_create_motor:
    aft = motor_io.load_motor(filename=filename)
    if re_solve:
        try:
            aft.reluctance_network.list_elements_lite = None
        except:
            pass
    
    aft = AxialFluxMotorType1()
    motor_io.save_motor(motor_obj=aft, filename=filename)
    aft.analysis_motor(max_relative_residual = 0.05,
                        max_iteration=50,
                        material_relax=0.4,
                        solve_cogging = True,
                        n_point = 25,
                        debug = True)

    motor_io.save_motor(motor_obj=aft, filename=filename)

if plot:
    
    flux_linkage = aft.record.flux_linkage
    back_emf     = aft.record.back_emf
    mst_data     = aft.record.mst_data  
    
    theta_pos = flux_linkage[-1, :]
    theta_mst = mst_data[-1, :]
    
    # Cấu hình màu sắc cho các pha
    colors = ['#d62728', '#2ca02c', '#1f77b4'] # Red (A), Green (B), Blue (C)
    
    # Tạo khung hình lớn với 4 biểu đồ con
    fig, axs = plt.subplots(2, 2, figsize=(14, 10), sharex=True)
    fig.suptitle(f"Motor Simulation Results: {filename} (at {aft.shaft_speed} RPM)", fontsize=16, fontweight='bold')

    # --- 1. BIỂU ĐỒ TỪ THÔNG LIÊN KẾT (FLUX LINKAGE) ---
    for j in range(aft.winding_data.phase):
        axs[0, 0].plot(theta_pos, flux_linkage[j, :], 
                       label=f'Phase {chr(65+j)}', color=colors[j % 3], linewidth=1.5)
    axs[0, 0].set_title("Magnetic Flux Linkage", fontweight='bold')
    axs[0, 0].set_ylabel("Flux (Wb)")
    axs[0, 0].grid(True, alpha=0.3)
    axs[0, 0].legend(loc='upper right')

    # --- 2. BIỂU ĐỒ SỨC ĐIỆN ĐỘNG (BACK-EMF) ---
    for j in range(aft.winding_data.phase):
        axs[0, 1].plot(theta_pos, back_emf[j, :], 
                       label=f'Phase {chr(65+j)}', color=colors[j % 3], linewidth=1.5)
    axs[0, 1].set_title(f"Back-EMF (Terminal)", fontweight='bold')
    axs[0, 1].set_ylabel("Voltage (V)")
    axs[0, 1].grid(True, alpha=0.3)
    axs[0, 1].legend(loc='upper right')

    # --- 3. BIỂU ĐỒ MÔ-MEN XOẮN (TORQUE TZ) ---
    torque_z = mst_data[3, :] # Index 3 theo hàm MST đã viết
    avg_torque = np.mean(torque_z)
    axs[1, 0].plot(theta_mst, torque_z, color='purple', linewidth=2, label='Electromagnetic Torque')
    axs[1, 0].axhline(y=avg_torque, color='black', linestyle='--', alpha=0.7, 
                      label=f'Average: {avg_torque:.2f} Nm')
    axs[1, 0].set_title("Electromagnetic Torque (Maxwell Stress)", fontweight='bold')
    axs[1, 0].set_ylabel("Torque (Nm)")
    axs[1, 0].set_xlabel("Rotor Position (rad)")
    axs[1, 0].grid(True, alpha=0.3)
    axs[1, 0].legend(loc='upper right')

    # --- 4. BIỂU ĐỒ LỰC DỌC TRỤC (AXIAL FORCE FZ) ---
    # Trong Axial Flux, lực Fz rất quan trọng để tính toán ổ bi
    force_z = mst_data[2, :] # Index 2 theo hàm MST
    axs[1, 1].plot(theta_mst, force_z, color='darkorange', linewidth=1.8, label='Axial Force')
    axs[1, 1].set_title("Axial Force (Fz)", fontweight='bold')
    axs[1, 1].set_ylabel("Force (N)")
    axs[1, 1].set_xlabel("Rotor Position (rad)")
    axs[1, 1].grid(True, alpha=0.3)
    axs[1, 1].legend(loc='upper right')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Tránh tiêu đề bị đè
    plt.show()

if show_reluctance:    
    aft.display()