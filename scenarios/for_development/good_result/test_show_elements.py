import paths
import numpy as np
import matplotlib.pyplot as plt
import math

from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io

RE_CREATE_MOTOR = True
FILENAME        = "AFT_Motor_Optimization"

aft = AxialFluxMotorType1()
aft.winding_data.turns = 25
aft.just_changed("winding_data")

aft.geometry_data.rotor.airgap = 0.5 * 1e-3
aft.geometry_data.rotor.magnet_length = 3 * 1e-3 
aft.just_changed("geometry")

aft.calculation_data.n_point = 31
aft.calculation_data.solve_cogging = True
aft.calculation_data.max_relative_residual = 0.01
aft.calculation_data.solve_only_1_step = False
aft.calculation_data.vectorized_optimization = True
aft.just_changed("calculation_data")

aft.adaptive_mesh_data.n_r_2 = 4
aft.adaptive_mesh_data.n_r_1 = 2
aft.adaptive_mesh_data.n_r_3 = 2
aft.adaptive_mesh_data.n_z_tooth_body = 4
aft.adaptive_mesh_data.n_z_tooth_tip_2 = 3
aft.just_changed("mesh")

aft.drive_data.i_rms = 10
aft.just_changed("drive")

#aft.require("reluctance_network")
#aft.reluctance_network.get_geometric_error()
#print(aft.reluctance_network.geometric_error)

aft.analysis_motor()
#aft.reluctance_network.show_elements()
aft.display()


# Trich xuat du lieu
flux = aft.record.flux_linkage
emf  = aft.record.back_emf
mst  = aft.record.mst_data
cogging = aft.record.cogging

# Truc goc (Radian)
theta_flux = flux[-1, :]
theta_mst  = mst[-1, :]
theta_cogging = cogging[-1, :]

# Cau hinh Figure
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Phân tích đặc tính máy điện Axial Flux", fontsize=16, fontweight='bold')
colors = ['#d62728', '#2ca02c', '#1f77b4'] 

# Bieu do 1: Tu thong lien ket (Flux Linkage)
for j in range(aft.winding_data.phase):
    axs[0, 0].plot(theta_flux, flux[j, :], color=colors[j % 3], 
                    label=f'Pha {chr(65+j)}', linewidth=1.5)
axs[0, 0].set_title("Từ thông liên kết (Flux Linkage)", fontweight='bold')
axs[0, 0].set_ylabel("Flux (Wb)")
axs[0, 0].grid(True, alpha=0.3)
axs[0, 0].legend()

# Bieu do 2: Suc dien dong (Back-EMF)
for j in range(aft.winding_data.phase):
    axs[0, 1].plot(theta_flux, emf[j, :], color=colors[j % 3], 
                    label=f'Pha {chr(65+j)}', linewidth=1.5)
axs[0, 1].set_title("Sức điện động (Back-EMF Terminal)", fontweight='bold')
axs[0, 1].set_ylabel("Voltage (V)")
axs[0, 1].grid(True, alpha=0.3)

# Bieu do 3: Mo-men dien tu (Maxwell Stress)
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

# Bieu do 4: Mo-men rang (Cogging Torque)
cogging_val = cogging[0, :]
axs[1, 1].plot(theta_cogging, cogging_val, color='brown', label='Cogging Torque')
axs[1, 1].set_title("Mô-men răng (Cogging Torque)", fontweight='bold')
axs[1, 1].set_ylabel("Torque (Nm)")
axs[1, 1].set_xlabel("Vị trí Rotor (rad)")
axs[1, 1].grid(True, alpha=0.3)
axs[1, 1].legend()



plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()


