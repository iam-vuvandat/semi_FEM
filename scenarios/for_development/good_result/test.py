import paths
import numpy as np
import matplotlib.pyplot as plt
import math
import time
from matplotlib.widgets import Slider
from mpl_toolkits.mplot3d import Axes3D

from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io

# 1. Khởi tạo đối tượng
aft = AxialFluxMotorType1()

# 2. Khai báo Material Data
aft.material_data.air = "default"
aft.material_data.magnet_type = "NdFe30"
aft.material_data.iron_type = "steel_1008"

# 3. Khai báo Winding Data
aft.winding_data.phase = 3
aft.winding_data.turns = 20
aft.winding_data.throw = 1
aft.winding_data.parallel_path = 1
aft.winding_data.winding_layer = 2
aft.winding_data.mmf_offset = 0.0
aft.just_changed("winding_data")

# 4. Khai báo Mechanical Data
aft.mechanical_data.shaft_speed = 3000

# 5. Khai báo Geometry Data - Stator
stator = aft.geometry_data.stator
stator.slot_number = 30
stator.stator_lam_dia = 150 * 1e-3
stator.stator_bore_dia = 70 * 1e-3
stator.slot_opening = 2 * 1e-3
stator.wdg_extension_inner = 0
stator.wdg_extension_outer = 0
stator.slot_width = 4 * 1e-3
stator.slot_depth = 15 * 1e-3
stator.slot_corner_radius = 0
stator.tooth_tip_depth = 2 * 1e-3
stator.tooth_tip_angle = 30
stator.stator_length = 25 * 1e-3

# 6. Khai báo Geometry Data - Rotor
rotor = aft.geometry_data.rotor
rotor.pole_number = 20
rotor.rotor_lam_dia = 150 * 1e-3
rotor.magnet_arc = 160
rotor.magnet_embed_depth = 5 * 1e-3
rotor.magnet_depth = 30 * 1e-3
rotor.magnet_segments = 1
rotor.banding_depth = 0 * 1e-3
rotor.shaft_dia = 0 * 1e-3
rotor.shaft_hole_diameter = 70 * 1e-3
rotor.airgap = 1.5 * 1e-3
rotor.magnet_length = 3 * 1e-3
rotor.rotor_length = 6 * 1e-3
aft.just_changed("geometry")

# 7. Khai báo Calculation Data
calc = aft.calculation_data
calc.convergence_settings.max_iteration = 50
calc.convergence_settings.max_relative_residual = 0.1 * 1e-2 # %
calc.convergence_settings.material_relax = 0.35

calc.general_options.n_point = 21
calc.general_options.solve_cogging = False
calc.general_options.solve_only_1_step = False
calc.general_options.vectorized_optimization = True
calc.general_options.get_geometric_error = False
calc.general_options.debug = True

calc.export_inductance_options.export_inductance = False
calc.export_inductance_options.current_min = 1.0
calc.export_inductance_options.current_max = 15.0
calc.export_inductance_options.current_resolution = 10
aft.just_changed("calculation_data")

# 8. Khai báo Adaptive Mesh Data
mesh = aft.adaptive_mesh_data
mesh.n_r_in = 1
mesh.n_r_1 = 3
mesh.n_r_2 = 6
mesh.n_r_3 = 3
mesh.n_r_out = 1
mesh.n_theta = 150
mesh.n_z_in_air = 1
mesh.n_z_rotor_yoke = 6
mesh.n_z_magnet = 5
mesh.n_z_airgap = 6
mesh.n_z_tooth_tip_1 = 5
mesh.n_z_tooth_tip_2 = 6
mesh.n_z_tooth_body = 8
mesh.n_z_stator_yoke = 6
mesh.n_z_out_air = 1
mesh.use_symmetry_factor = True
mesh.periodic_boundary = True
aft.just_changed("mesh")

# 9. Khai báo Drive Data
aft.drive_data.i_rms = 20.0
aft.drive_data.phase_advanced = 0.0
aft.just_changed("drive")

# 10. Khai báo Maxwell Export Option
export = aft.maxwell_export_option
export.ansys_electronic_version = "2025.2"
export.use_default_option = True
export.custom_option.mesh_setting.band_mapping_angle = math.pi / 180
export.custom_option.motion_setting.shaft_speed = 3000
export.solver_option.solve_immediately = False
export.solver_option.solve_only_1_step = False

# --- Thực thi mô phỏng ---
aft.require("geometry")
aft.geometry.show()

start_time_for_semiFEM = time.perf_counter()
aft.analysis_motor()
stop_time_for_semiFEM = time.perf_counter()
total_time_for_semiFEM = stop_time_for_semiFEM - start_time_for_semiFEM

print(f"Total time for semiFEM: {total_time_for_semiFEM}")

# --- Hậu xử lý kết quả ---
flux = aft.record.flux_linkage
emf  = aft.record.back_emf
mst  = aft.record.mst_data
cogging = aft.record.cogging
currents = aft.record.currents
p_mech_values = aft.record.mechanical_power[0, :]
theta_p_mech  = aft.record.mechanical_power[1, :]
avg_p_mech    = aft.record.average_mechanical_power

theta_flux = flux[-1, :]
theta_mst  = mst[-1, :]
theta_cogging = cogging[-1, :]
theta_curr = currents[-1, :]

num_plots = 7
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

# Plot 0: Flux Linkage
axs[0].plot(theta_flux, flux[0, :], 'k--', label='$\Psi_d$', linewidth=1.5)
axs[0].plot(theta_flux, flux[1, :], 'k-', label='$\Psi_q$', linewidth=1.5)
for j in range(aft.winding_data.phase):
    axs[0].plot(theta_flux, flux[2 + j, :], color=colors[j % 3], label=f'Pha {chr(65+j)}', alpha=0.7)
axs[0].set_title("Từ thông liên kết (Flux Linkage)", fontweight='bold')
axs[0].set_ylabel("Flux (Wb)")
axs[0].legend(loc='upper right', fontsize='small', ncol=2)
axs[0].grid(True, alpha=0.3)

# Plot 1: Back-EMF
for j in range(aft.winding_data.phase):
    axs[1].plot(theta_flux, emf[j, :], color=colors[j % 3], label=f'Pha {chr(65+j)}')
axs[1].set_title("Sức điện động (Back-EMF)", fontweight='bold')
axs[1].set_ylabel("Voltage (V)")
axs[1].grid(True, alpha=0.3)

# Plot 2: Torque
torque_z = mst[3, :]
avg_torque = np.mean(torque_z)
axs[2].plot(theta_mst, torque_z, color='purple')
axs[2].axhline(y=avg_torque, color='black', linestyle='--', label=f'Avg: {avg_torque:.2f} Nm')
axs[2].set_title("Mô-men điện từ (Maxwell Stress)", fontweight='bold')
axs[2].set_ylabel("Torque (Nm)")
axs[2].set_ylim(bottom=0)
axs[2].legend(loc='upper right')
axs[2].grid(True, alpha=0.3)

# Plot 3: Axial Force
axial_force = mst[2, :]
avg_axial = np.mean(axial_force)
axs[3].plot(theta_mst, axial_force, color='darkcyan')
axs[3].axhline(y=avg_axial, color='black', linestyle='--', label=f'Avg: {avg_axial:.2f} N')
axs[3].set_title("Lực dọc trục (Axial Force)", fontweight='bold')
axs[3].set_ylabel("Force (N)")
axs[3].set_ylim(bottom=0)
axs[3].legend(loc='upper right')
axs[3].grid(True, alpha=0.3)

# Plot 4: Cogging
axs[4].plot(theta_cogging, cogging[0, :], color='brown')
axs[4].set_title("Mô-men răng (Cogging Torque)", fontweight='bold')
axs[4].set_ylabel("Torque (Nm)")
axs[4].grid(True, alpha=0.3)

# Plot 5: Currents
axs[5].plot(theta_curr, currents[0, :], 'r--', label='$I_d$', linewidth=1.5)
axs[5].plot(theta_curr, currents[1, :], 'b-', label='$I_q$', linewidth=1.5)
for j in range(aft.winding_data.phase):
    axs[5].plot(theta_curr, currents[2 + j, :], color=colors[j % 3], label=f'Phase {chr(65+j)}', alpha=0.7)
axs[5].set_title("Dòng điện (Currents)", fontweight='bold')
axs[5].set_ylabel("Current (A)")
axs[5].legend(loc='upper right', fontsize='small', ncol=2)
axs[5].grid(True, alpha=0.3)

# Plot 6: Mechanical Power
axs[6].plot(theta_p_mech, p_mech_values, color='forestgreen', linewidth=1.5, label='P_mech')
if avg_p_mech is not None:
    axs[6].axhline(y=avg_p_mech, color='red', linestyle='--', label=f'Avg: {avg_p_mech:.2f} W')
axs[6].set_title("Công suất cơ học (Mechanical Power)", fontweight='bold')
axs[6].set_ylabel("Power (W)")
axs[6].set_xlabel("Vị trí Rotor (rad)")
axs[6].set_ylim(bottom=0)
axs[6].legend(loc='upper right')
axs[6].grid(True, alpha=0.3)

# Plot 3D Inductance Map (Optional)
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
    ax2 = fig3d.add_subplot(122, projection='3d')
    surf2 = ax2.plot_surface(ID, IQ, lq_map, cmap='plasma', edgecolor='none', alpha=0.9)
    ax2.set_title("Bản đồ điện cảm $L_q$ (mH)", fontweight='bold')

plt.show()
aft.display()