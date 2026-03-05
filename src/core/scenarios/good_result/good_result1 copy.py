import paths
import numpy as np
import matplotlib.pyplot as plt
import math

from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1



aft = AxialFluxMotorType1()
aft.require("drive")

aft.analysis_motor()

   
    
    
flux = aft.record.flux_linkage
emf  = aft.record.back_emf
mst  = aft.record.mst_data  # Dữ liệu này đã được duplicate_data (2 chu kỳ)

# Trục góc (Radian)
theta_flux = flux[-1, :]
theta_mst  = mst[-1, :]

# Cấu hình Figure
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("abc")
colors = ['#d62728', '#2ca02c', '#1f77b4'] # Đỏ, Lục, Lam đại diện 3 pha

# Biểu đồ 1: Từ thông liên kết (Flux Linkage)
for j in range(aft.winding_data.phase):
    axs[0, 0].plot(theta_flux, flux[j, :], color=colors[j % 3], 
                    label=f'Pha {chr(65+j)}', linewidth=1.5)
axs[0, 0].set_title("Từ thông liên kết (Flux Linkage)", fontweight='bold')
axs[0, 0].set_ylabel("Flux (Wb)")
axs[0, 0].grid(True, alpha=0.3)
axs[0, 0].legend()

# Biểu đồ 2: Sức điện động (Back-EMF)
for j in range(aft.winding_data.phase):
    axs[0, 1].plot(theta_flux, emf[j, :], color=colors[j % 3], 
                    label=f'Pha {chr(65+j)}', linewidth=1.5)
axs[0, 1].set_title("Sức điện động (Back-EMF Terminal)", fontweight='bold')
axs[0, 1].set_ylabel("Voltage (V)")
axs[0, 1].grid(True, alpha=0.3)

# Biểu đồ 3: Mô-men xoắn (Torque) - 2 chu kỳ
torque_z = mst[3, :]
avg_torque = np.mean(torque_z)
axs[1, 0].plot(theta_mst, torque_z, color='purple', label='Torque')
axs[1, 0].axhline(y=avg_torque, color='black', linestyle='--', alpha=0.7, 
                    label=f'Avg: {avg_torque:.2f} Nm')
axs[1, 0].set_title("Mô-men điện từ (Maxwell Stress)", fontweight='bold')
axs[1, 0].set_ylabel("Torque (Nm)")
axs[1, 0].set_xlabel("Vị trí Rotor (rad)")
axs[1, 0].grid(True, alpha=0.3)
axs[1, 0].legend()

# Biểu đồ 4: Lực dọc trục (Axial Force) - 2 chu kỳ
force_z = mst[2, :]
axs[1, 1].plot(theta_mst, force_z, color='darkorange', label='Axial Force')
axs[1, 1].set_title("Lực dọc trục (Fz)", fontweight='bold')
axs[1, 1].set_ylabel("Force (N)")
axs[1, 1].set_xlabel("Vị trí Rotor (rad)")
axs[1, 1].grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()


aft.display()