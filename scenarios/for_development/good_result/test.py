import paths
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d import Axes3D

from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io

aft = AxialFluxMotorType1()
aft.winding_data.turns = 30
aft.just_changed("winding_data")

aft.geometry_data.rotor.airgap = 0.5 * 1e-3
aft.geometry_data.rotor.magnet_length = 3 * 1e-3 
aft.just_changed("geometry")

calc = aft.calculation_data
calc.general_options.n_point = 25
calc.general_options.solve_cogging = True
calc.general_options.solve_only_1_step = False
calc.general_options.vectorized_optimization = True
calc.general_options.debug = True

calc.convergence_settings.max_relative_residual = 0.1 * 1e-2 # %
calc.convergence_settings.max_iteration = 50
calc.convergence_settings.material_relax = 0.35

calc.export_inductance_options.export_inductance = True
calc.export_inductance_options.current_min = 1
calc.export_inductance_options.current_max = 15
calc.export_inductance_options.current_resolution = 10 

aft.just_changed("calculation_data")

aft.adaptive_mesh_data.n_r_2 = 3
aft.adaptive_mesh_data.n_r_1 = 3
aft.adaptive_mesh_data.n_r_3 = 3
aft.adaptive_mesh_data.n_z_tooth_body = 3
aft.adaptive_mesh_data.n_z_tooth_tip_2 = 3
aft.just_changed("mesh")

aft.drive_data.i_rms = 10.0
aft.just_changed("drive")

aft.analysis_motor()

flux = aft.record.flux_linkage
emf  = aft.record.back_emf
mst  = aft.record.mst_data
cogging = aft.record.cogging
currents = aft.record.currents

theta_flux = flux[-1, :]
theta_mst  = mst[-1, :]
theta_cogging = cogging[-1, :]
theta_curr = currents[-1, :]

num_plots = 6
fig = plt.figure(figsize=(12, 9))
plt.subplots_adjust(left=0.1, right=0.85, top=0.95, bottom=0.05)

plot_height = 0.4
total_height = num_plots * plot_height

axs = []
for i in range(num_plots):
    ax = fig.add_axes([0.1, 1.0 - (i+1)*plot_height, 0.75, plot_height * 0.8])
    axs.append(ax)

ax_slider = fig.add_axes([0.9, 0.1, 0.03, 0.8], facecolor='#f0f0f0')
slider = Slider(ax_slider, '', 0, total_height - 1.0, valinit=total_height - 1.0, orientation='vertical')

def update(val):
    pos = slider.val
    for i, ax in enumerate(axs):
        new_y = (1.0 - (i+1)*plot_height) + (total_height - 1.0 - pos)
        ax.set_position([0.1, new_y, 0.75, plot_height * 0.8])
    fig.canvas.draw_idle()

slider.on_changed(update)

colors = ['#d62728', '#2ca02c', '#1f77b4']

axs[0].plot(theta_flux, flux[0, :], 'k--', label='$\Psi_d$', linewidth=1.5)
axs[0].plot(theta_flux, flux[1, :], 'k-', label='$\Psi_q$', linewidth=1.5)
for j in range(aft.winding_data.phase):
    axs[0].plot(theta_flux, flux[2 + j, :], color=colors[j % 3], label=f'Pha {chr(65+j)}', alpha=0.7)
axs[0].set_title("Từ thông liên kết (Flux Linkage)", fontweight='bold')
axs[0].set_ylabel("Flux (Wb)")
axs[0].legend(loc='upper right', fontsize='small', ncol=2)
axs[0].grid(True, alpha=0.3)

for j in range(aft.winding_data.phase):
    axs[1].plot(theta_flux, emf[j, :], color=colors[j % 3], label=f'Pha {chr(65+j)}')
axs[1].set_title("Sức điện động (Back-EMF)", fontweight='bold')
axs[1].set_ylabel("Voltage (V)")
axs[1].grid(True, alpha=0.3)

torque_z = mst[3, :]
avg_torque = np.mean(torque_z)
axs[2].plot(theta_mst, torque_z, color='purple')
axs[2].axhline(y=avg_torque, color='black', linestyle='--', label=f'Avg: {avg_torque:.2f} Nm')
axs[2].set_title("Mô-men điện từ (Maxwell Stress)", fontweight='bold')
axs[2].set_ylabel("Torque (Nm)")
axs[2].legend(loc='upper right')
axs[2].grid(True, alpha=0.3)

axial_force = mst[2, :]
avg_axial = np.mean(axial_force)
axs[3].plot(theta_mst, axial_force, color='darkcyan')
axs[3].axhline(y=avg_axial, color='black', linestyle='--', label=f'Avg: {avg_axial:.2f} N')
axs[3].set_title("Lực dọc trục (Axial Force)", fontweight='bold')
axs[3].set_ylabel("Force (N)")
axs[3].legend(loc='upper right')
axs[3].grid(True, alpha=0.3)

axs[4].plot(theta_cogging, cogging[0, :], color='brown')
axs[4].set_title("Mô-men răng (Cogging Torque)", fontweight='bold')
axs[4].set_ylabel("Torque (Nm)")
axs[4].grid(True, alpha=0.3)

axs[5].plot(theta_curr, currents[0, :], 'r--', label='$I_d$', linewidth=1.5)
axs[5].plot(theta_curr, currents[1, :], 'b-', label='$I_q$', linewidth=1.5)
for j in range(aft.winding_data.phase):
    axs[5].plot(theta_curr, currents[2 + j, :], color=colors[j % 3], label=f'Phase {chr(65+j)}', alpha=0.7)
axs[5].set_title("Dòng điện (Currents)", fontweight='bold')
axs[5].set_ylabel("Current (A)")
axs[5].set_xlabel("Vị trí Rotor (rad)")
axs[5].legend(loc='upper right', fontsize='small', ncol=2)
axs[5].grid(True, alpha=0.3)

if calc.export_inductance_options.export_inductance:
    id_grid = aft.record.id_grid
    iq_grid = aft.record.iq_grid
    ld_map = aft.record.ld_map * 1000 
    lq_map = aft.record.lq_map * 1000 

    ld_map[ld_map == 0] = np.nan
    lq_map[lq_map == 0] = np.nan
    
    ID, IQ = np.meshgrid(id_grid, iq_grid, indexing='ij')

    fig3d = plt.figure(figsize=(14, 6))
    
    ax1 = fig3d.add_subplot(121, projection='3d')
    surf1 = ax1.plot_surface(ID, IQ, ld_map, cmap='viridis', edgecolor='none', alpha=0.9)
    ax1.set_title("Bản đồ điện cảm $L_d$ (mH)", fontweight='bold')
    ax1.set_xlabel("$I_d$ (A)")
    ax1.set_ylabel("$I_q$ (A)")
    fig3d.colorbar(surf1, ax=ax1, shrink=0.5, aspect=10)

    ax2 = fig3d.add_subplot(122, projection='3d')
    surf2 = ax2.plot_surface(ID, IQ, lq_map, cmap='plasma', edgecolor='none', alpha=0.9)
    ax2.set_title("Bản đồ điện cảm $L_q$ (mH)", fontweight='bold')
    ax2.set_xlabel("$I_d$ (A)")
    ax2.set_ylabel("$I_q$ (A)")
    fig3d.colorbar(surf2, ax=ax2, shrink=0.5, aspect=10)

plt.show()
aft.display()