import paths
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.widgets import Slider

from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io

RE_CREATE_MOTOR = True
FILENAME        = "AFT_Motor_Optimization"

aft = AxialFluxMotorType1()
aft.winding_data.turns = 30
aft.just_changed("winding_data")

aft.geometry_data.rotor.airgap = 0.5 * 1e-3
aft.geometry_data.rotor.magnet_length = 3 * 1e-3 
aft.just_changed("geometry")

aft.calculation_data.n_point = 25
aft.calculation_data.solve_cogging = False
aft.calculation_data.max_relative_residual = 0.005
aft.calculation_data.solve_only_1_step = False
aft.calculation_data.vectorized_optimization = True
aft.just_changed("calculation_data")

aft.adaptive_mesh_data.n_r_2 = 6
aft.adaptive_mesh_data.n_r_1 = 3
aft.adaptive_mesh_data.n_r_3 = 3
aft.adaptive_mesh_data.n_z_tooth_body = 6
aft.adaptive_mesh_data.n_z_tooth_tip_2 = 4
aft.just_changed("mesh")

aft.drive_data.i_rms = 15
aft.just_changed("drive")

aft.analysis_motor()

# Trich xuat du lieu
flux = aft.record.flux_linkage
emf  = aft.record.back_emf
mst  = aft.record.mst_data
cogging = aft.record.cogging
currents = aft.record.currents

theta_flux = flux[-1, :]
theta_mst  = mst[-1, :]
theta_cogging = cogging[-1, :]
theta_curr = currents[-1, :]

# ==============================================================================
# CAU HINH CUA SO DO THI CUON (SCROLLABLE)
# ==============================================================================
num_plots = 6
fig = plt.figure(figsize=(12, 8))
plt.subplots_adjust(left=0.1, right=0.85, top=0.95, bottom=0.05)

# Chieu cao ao cua vung ve (moi plot cao 0.4 don vi hinh hoc)
plot_height = 0.4
total_height = num_plots * plot_height

# Tao danh sach cac axes xep chong len nhau theo chieu doc
axs = []
for i in range(num_plots):
    # Vi tri ban dau: x_start, y_start, width, height
    ax = fig.add_axes([0.1, 1.0 - (i+1)*plot_height, 0.75, plot_height * 0.8])
    axs.append(ax)

# Them thanh truot (Slider) ben phai
ax_slider = fig.add_axes([0.9, 0.1, 0.03, 0.8], facecolor='#f0f0f0')
slider = Slider(ax_slider, '', 0, total_height - 1.0, valinit=total_height - 1.0, orientation='vertical')

def update(val):
    pos = slider.val
    for i, ax in enumerate(axs):
        # Cap nhat vi tri y dua tren gia tri thanh truot
        new_y = (1.0 - (i+1)*plot_height) + (total_height - 1.0 - pos)
        ax.set_position([0.1, new_y, 0.75, plot_height * 0.8])
    fig.canvas.draw_idle()

slider.on_changed(update)

colors = ['#d62728', '#2ca02c', '#1f77b4']

# 1. Tu thong lien ket
for j in range(aft.winding_data.phase):
    axs[0].plot(theta_flux, flux[j, :], color=colors[j % 3], label=f'Pha {chr(65+j)}')
axs[0].set_title("Từ thông liên kết (Flux Linkage)", fontweight='bold')
axs[0].set_ylabel("Flux (Wb)")
axs[0].legend(loc='upper right')
axs[0].grid(True, alpha=0.3)

# 2. Suc dien dong
for j in range(aft.winding_data.phase):
    axs[1].plot(theta_flux, emf[j, :], color=colors[j % 3], label=f'Pha {chr(65+j)}')
axs[1].set_title("Sức điện động (Back-EMF)", fontweight='bold')
axs[1].set_ylabel("Voltage (V)")
axs[1].grid(True, alpha=0.3)

# 3. Mo-men dien tu
torque_z = mst[3, :]
avg_torque = np.mean(torque_z)
axs[2].plot(theta_mst, torque_z, color='purple')
axs[2].axhline(y=avg_torque, color='black', linestyle='--', label=f'Avg: {avg_torque:.2f} Nm')
axs[2].set_title("Mô-men điện từ (Maxwell Stress)", fontweight='bold')
axs[2].set_ylabel("Torque (Nm)")
axs[2].legend(loc='upper right')
axs[2].grid(True, alpha=0.3)

# 4. Mo-men rang
axs[3].plot(theta_cogging, cogging[0, :], color='brown')
axs[3].set_title("Mô-men răng (Cogging Torque)", fontweight='bold')
axs[3].set_ylabel("Torque (Nm)")
axs[3].grid(True, alpha=0.3)

# 5. Dong dien cac pha
for j in range(aft.winding_data.phase):
    axs[4].plot(theta_curr, currents[2 + j, :], color=colors[j % 3], label=f'Phase {chr(65+j)}')
axs[4].set_title("Dòng điện các pha (abc)", fontweight='bold')
axs[4].set_ylabel("Current (A)")
axs[4].grid(True, alpha=0.3)

# 6. Dong dien Id - Iq
axs[5].plot(theta_curr, currents[0, :], 'r--', label='Id (Direct)')
axs[5].plot(theta_curr, currents[1, :], 'b-', label='Iq (Quadrature)')
axs[5].set_title("Dòng điện thành phần Id - Iq", fontweight='bold')
axs[5].set_ylabel("Current (A)")
axs[5].set_xlabel("Vị trí Rotor (rad)")
axs[5].legend(loc='upper right')
axs[5].grid(True, alpha=0.3)

plt.show()
aft.display()