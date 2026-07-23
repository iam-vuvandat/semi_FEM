import os
import paths
import numpy as np
import matplotlib.pyplot as plt

from src.core.storage.core.MotorIO import MotorIO
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style

# -------------------------------------------------------------------------
# 1. KHỞI TẠO VÀ LOAD DỮ LIỆU
# -------------------------------------------------------------------------
io = MotorIO()
s = apply_journal_style()
fig_width = 10
fig_height = fig_width / 1.5

number_of_configuation = 5
file_name_array = [f"motor_for_paper{i}" for i in range(number_of_configuation)]

motor_array = []
for i in range(number_of_configuation):
    aft = io.load(path=file_name_array[i])
    motor_array.append(aft)

# Lấy mốc cấu hình mịn nhất làm reference
reference_aft = motor_array[-1]
reference_aft.require('mesh')
record_ref = reference_aft.record
shaft_speed = (reference_aft.mechanical_data.shaft_speed * np.pi * 2) / 60

# Trích xuất số lượng phần tử MBGRN
table_data = []
for idx, aft in enumerate(motor_array):
    aft.require('mesh')
    table_data.append((idx, aft.mesh.n_cells_r, aft.mesh.n_cells_t, aft.mesh.n_cells_z, aft.mesh.total_cells))

config_index = [row[0] + 1 for row in table_data]
total_elements = [row[4] for row in table_data]


# =========================================================================
# FIGURE 1: TOTAL MESH CELLS (3D-MBGRN)
# =========================================================================
plt.figure(figsize=(fig_width, fig_height))
plt.plot(config_index, total_elements, marker='o', color=s.colors[0], linewidth=2.0, markersize=8)
plt.xlabel('Mesh Configuration Index', fontsize=s.label_size)
plt.ylabel('Total Mesh Cells', fontsize=s.label_size)
plt.title('Total Mesh Cells vs Configuration Index', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.tight_layout()
plt.show()


# =========================================================================
# BỘ ĐỒ THỊ 1: DẠNG SÓNG CHỒNG PHỔ CỦA DUY NHẤT 3D-MBGRN (5 FIGURES)
# =========================================================================

# --- MBGRN Fig 1: Airgap Flux Density B_z ---
plt.figure(figsize=(fig_width, fig_height))
for i, aft in enumerate(motor_array):
    aft.require('mesh')
    record = aft.record
    if hasattr(record, 'airgap_flux_density') and record.airgap_flux_density is not None:
        x_axis = record.airgap_flux_density[4, :]
        B_z = record.airgap_flux_density[2, :]
        total_cells = aft.mesh.total_cells
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            x_axis, B_z, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(x_axis) // 25),
            markersize=7, linewidth=lw, 
            label=f"MBGRN Mesh {i+1} ({total_cells:,} cells)"
        )
plt.xlabel('Angular Position (rad)', fontsize=s.label_size)
plt.ylabel('Airgap Flux Density $B_z$ (T)', fontsize=s.label_size)
plt.title('3D-MBGRN Airgap Axial Flux Density ($B_z$) Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='upper right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()

# --- MBGRN Fig 2: Flux Linkage On-Load ---
plt.figure(figsize=(fig_width, fig_height))
for i, aft in enumerate(motor_array):
    aft.require('mesh')
    record = aft.record
    if hasattr(record, 'flux_linkage') and record.flux_linkage is not None:
        shaft_speed_i = (aft.mechanical_data.shaft_speed * np.pi * 2) / 60
        theta_data = record.flux_linkage[-1, :]
        time_ms = (theta_data / shaft_speed_i) * 1e3
        psi_a = record.flux_linkage[2, :]
        total_cells = aft.mesh.total_cells
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            time_ms, psi_a, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(time_ms) // 25),
            markersize=7, linewidth=lw, 
            label=f"MBGRN Mesh {i+1} ({total_cells:,} cells)"
        )
plt.xlabel('Time (ms)', fontsize=s.label_size)
plt.ylabel('Flux Linkage $\Psi_a$ (Wb)', fontsize=s.label_size)
plt.title('3D-MBGRN Phase A On-Load Flux Linkage Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()

# --- MBGRN Fig 3: Torque On-Load ---
plt.figure(figsize=(fig_width, fig_height))
for i, aft in enumerate(motor_array):
    aft.require('mesh')
    record = aft.record
    if hasattr(record, 'torque') and record.torque is not None:
        shaft_speed_i = (aft.mechanical_data.shaft_speed * np.pi * 2) / 60
        theta_data = record.torque[-1, :]
        time_ms = (theta_data / shaft_speed_i) * 1e3
        val_torque = record.torque[0, :]
        total_cells = aft.mesh.total_cells
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            time_ms, val_torque, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(time_ms) // 25),
            markersize=7, linewidth=lw, 
            label=f"MBGRN Mesh {i+1} ({total_cells:,} cells)"
        )
plt.xlabel('Time (ms)', fontsize=s.label_size)
plt.ylabel('Torque (Nm)', fontsize=s.label_size)
plt.title('3D-MBGRN On-Load Torque Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()

# --- MBGRN Fig 4: Cogging Torque ---
plt.figure(figsize=(fig_width, fig_height))
for i, aft in enumerate(motor_array):
    aft.require('mesh')
    record = aft.record
    if hasattr(record, 'cogging') and record.cogging is not None:
        shaft_speed_i = (aft.mechanical_data.shaft_speed * np.pi * 2) / 60
        theta_data = record.cogging[1, :]
        time_ms = (theta_data / shaft_speed_i) * 1e3
        val_cogging = record.cogging[0, :]
        total_cells = aft.mesh.total_cells
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            time_ms, val_cogging, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(time_ms) // 25),
            markersize=7, linewidth=lw, 
            label=f"MBGRN Mesh {i+1} ({total_cells:,} cells)"
        )
plt.xlabel('Time (ms)', fontsize=s.label_size)
plt.ylabel('Cogging Torque (Nm)', fontsize=s.label_size)
plt.title('3D-MBGRN Cogging Torque Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()

# --- MBGRN Fig 5: Axial Force ---
plt.figure(figsize=(fig_width, fig_height))
for i, aft in enumerate(motor_array):
    aft.require('mesh')
    record = aft.record
    if hasattr(record, 'axial_force') and record.axial_force is not None:
        shaft_speed_i = (aft.mechanical_data.shaft_speed * np.pi * 2) / 60
        theta_data = record.axial_force[-1, :]
        time_ms = (theta_data / shaft_speed_i) * 1e3
        val_force = record.axial_force[0, :]
        total_cells = aft.mesh.total_cells
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            time_ms, val_force, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(time_ms) // 25),
            markersize=7, linewidth=lw, 
            label=f"MBGRN Mesh {i+1} ({total_cells:,} cells)"
        )
plt.xlabel('Time (ms)', fontsize=s.label_size)
plt.ylabel('Axial Force (N)', fontsize=s.label_size)
plt.title('3D-MBGRN Axial Force Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()


# =========================================================================
# BỘ ĐỒ THỊ 2: DẠNG SÓNG CHỒNG PHỔ CỦA DUY NHẤT 3D-FEM (5 FIGURES)
# =========================================================================

# --- FEM Fig 1: Airgap Flux Density B_z ---
plt.figure(figsize=(fig_width, fig_height))
for i, aft in enumerate(motor_array):
    record = aft.record
    if hasattr(record, 'airgap_flux_density_fem') and record.airgap_flux_density_fem is not None:
        x_fem = record.airgap_flux_density_fem[4, :]
        B_z_fem = record.airgap_flux_density_fem[2, :]
        fem_tets = record.mesh_data_fem.total_elements if hasattr(record, 'mesh_data_fem') and record.mesh_data_fem is not None else 0
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            x_fem, B_z_fem, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(x_fem) // 25),
            markersize=7, linewidth=lw, 
            label=f"3D-FEM Step {i+1} ({fem_tets:,} tets)" if fem_tets > 0 else f"3D-FEM Step {i+1}"
        )
plt.xlabel('Angular Position (rad)', fontsize=s.label_size)
plt.ylabel('Airgap Flux Density $B_z$ (T)', fontsize=s.label_size)
plt.title('3D-FEM Airgap Axial Flux Density ($B_z$) Mesh Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='upper right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()

# --- FEM Fig 2: Flux Linkage On-Load ---
plt.figure(figsize=(fig_width, fig_height))
for i, aft in enumerate(motor_array):
    record = aft.record
    if hasattr(record, 'flux_linkage_fem') and record.flux_linkage_fem is not None:
        shaft_speed_i = (aft.mechanical_data.shaft_speed * np.pi * 2) / 60
        theta_fem = record.flux_linkage_fem[-1, :]
        time_ms_fem = (theta_fem / shaft_speed_i) * 1e3
        psi_a_fem = record.flux_linkage_fem[2, :]
        fem_tets = record.mesh_data_fem.total_elements if hasattr(record, 'mesh_data_fem') and record.mesh_data_fem is not None else 0
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            time_ms_fem, psi_a_fem, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(time_ms_fem) // 25),
            markersize=7, linewidth=lw, 
            label=f"3D-FEM Step {i+1} ({fem_tets:,} tets)" if fem_tets > 0 else f"3D-FEM Step {i+1}"
        )
plt.xlabel('Time (ms)', fontsize=s.label_size)
plt.ylabel('Flux Linkage $\Psi_a$ (Wb)', fontsize=s.label_size)
plt.title('3D-FEM Phase A On-Load Flux Linkage Mesh Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()

# --- FEM Fig 3: Torque On-Load ---
plt.figure(figsize=(fig_width, fig_height))
for i, aft in enumerate(motor_array):
    record = aft.record
    if hasattr(record, 'torque_fem') and record.torque_fem is not None:
        shaft_speed_i = (aft.mechanical_data.shaft_speed * np.pi * 2) / 60
        theta_fem = record.torque_fem[-1, :]
        time_ms_fem = (theta_fem / shaft_speed_i) * 1e3
        val_torque_fem = record.torque_fem[0, :]
        fem_tets = record.mesh_data_fem.total_elements if hasattr(record, 'mesh_data_fem') and record.mesh_data_fem is not None else 0
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            time_ms_fem, val_torque_fem, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(time_ms_fem) // 25),
            markersize=7, linewidth=lw, 
            label=f"3D-FEM Step {i+1} ({fem_tets:,} tets)" if fem_tets > 0 else f"3D-FEM Step {i+1}"
        )
plt.xlabel('Time (ms)', fontsize=s.label_size)
plt.ylabel('Torque (Nm)', fontsize=s.label_size)
plt.title('3D-FEM On-Load Torque Mesh Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()

# --- FEM Fig 4: Cogging Torque ---
plt.figure(figsize=(fig_width, fig_height))
for i, aft in enumerate(motor_array):
    record = aft.record
    if hasattr(record, 'cogging_fem') and record.cogging_fem is not None:
        shaft_speed_i = (aft.mechanical_data.shaft_speed * np.pi * 2) / 60
        theta_fem = record.cogging_fem[1, :]
        time_ms_fem = (theta_fem / shaft_speed_i) * 1e3
        val_cogging_fem = record.cogging_fem[0, :]
        fem_tets = record.mesh_data_fem.total_elements if hasattr(record, 'mesh_data_fem') and record.mesh_data_fem is not None else 0
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            time_ms_fem, val_cogging_fem, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(time_ms_fem) // 25),
            markersize=7, linewidth=lw, 
            label=f"3D-FEM Step {i+1} ({fem_tets:,} tets)" if fem_tets > 0 else f"3D-FEM Step {i+1}"
        )
plt.xlabel('Time (ms)', fontsize=s.label_size)
plt.ylabel('Cogging Torque (Nm)', fontsize=s.label_size)
plt.title('3D-FEM Cogging Torque Mesh Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()

# --- FEM Fig 5: Axial Force ---
plt.figure(figsize=(fig_width, fig_height))
for i, aft in enumerate(motor_array):
    record = aft.record
    if hasattr(record, 'axial_force_fem') and record.axial_force_fem is not None:
        shaft_speed_i = (aft.mechanical_data.shaft_speed * np.pi * 2) / 60
        theta_fem = record.axial_force_fem[-1, :]
        time_ms_fem = (theta_fem / shaft_speed_i) * 1e3
        val_force_fem = record.axial_force_fem[0, :]
        fem_tets = record.mesh_data_fem.total_elements if hasattr(record, 'mesh_data_fem') and record.mesh_data_fem is not None else 0
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            time_ms_fem, val_force_fem, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(time_ms_fem) // 25),
            markersize=7, linewidth=lw, 
            label=f"3D-FEM Step {i+1} ({fem_tets:,} tets)" if fem_tets > 0 else f"3D-FEM Step {i+1}"
        )
plt.xlabel('Time (ms)', fontsize=s.label_size)
plt.ylabel('Axial Force (N)', fontsize=s.label_size)
plt.title('3D-FEM Axial Force Mesh Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()


# =========================================================================
# BỘ ĐỒ THỊ 3: TỐC ĐỘ TỰ HỘI TỤ (SELF-CONVERGENCE RATE NRMSE)
# =========================================================================

# --- MBGRN Self-Convergence ---
mbgrn_ref_B_z = reference_aft.record.airgap_flux_density
mbgrn_ref_psi = reference_aft.record.flux_linkage
mbgrn_ref_torque = reference_aft.record.torque

nrmse_mbgrn_B_z = []
nrmse_mbgrn_psi = []
nrmse_mbgrn_torque = []

for i in range(number_of_configuation):
    aft = motor_array[i]
    aft.require('mesh')
    
    data_pred_B_z = aft.record.airgap_flux_density
    data_pred_psi = aft.record.flux_linkage
    data_pred_torque = aft.record.torque
    
    err_B_z = get_waveform_nrmse(data_true=mbgrn_ref_B_z, data_pred=data_pred_B_z, num_points=200, row_index=2)
    err_psi = get_waveform_nrmse(data_true=mbgrn_ref_psi, data_pred=data_pred_psi, num_points=200, row_index=2)
    err_torque = get_waveform_nrmse(data_true=mbgrn_ref_torque, data_pred=data_pred_torque, num_points=200, row_index=0)
    
    nrmse_mbgrn_B_z.append(err_B_z)
    nrmse_mbgrn_psi.append(err_psi)
    nrmse_mbgrn_torque.append(err_torque)

plt.figure(figsize=(fig_width, fig_height))
plt.plot(total_elements[:-1], nrmse_mbgrn_B_z[:-1], color=s.colors[0], marker='o', linestyle='-', linewidth=2.5, markersize=9, label=r'NRMSE of $B_z$')
plt.plot(total_elements[:-1], nrmse_mbgrn_psi[:-1], color=s.colors[2], marker='s', linestyle='-', linewidth=2.5, markersize=9, label=r'NRMSE of $\Psi_a$')
plt.plot(total_elements[:-1], nrmse_mbgrn_torque[:-1], color=s.colors[1], marker='^', linestyle='-', linewidth=2.5, markersize=9, label='NRMSE of Torque')
plt.xlabel('Total MBGRN Elements ($Q_E$)', fontsize=s.label_size)
plt.ylabel('MBGRN Self-Convergence NRMSE (%)', fontsize=s.label_size)
plt.title('3D-MBGRN Mesh Self-Convergence Rate Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='upper right', fontsize=s.legend_size)
plt.tight_layout()
plt.show()

# --- FEM Self-Convergence ---
if hasattr(record_ref, 'airgap_flux_density_fem') and record_ref.airgap_flux_density_fem is not None:
    fem_ref_B_z = record_ref.airgap_flux_density_fem
    fem_ref_psi = record_ref.flux_linkage_fem
    fem_ref_torque = record_ref.torque_fem

    fem_tets_array = []
    nrmse_fem_B_z = []
    nrmse_fem_psi = []
    nrmse_fem_torque = []

    for i in range(number_of_configuation):
        aft = motor_array[i]
        
        fem_pred_B_z = aft.record.airgap_flux_density_fem
        fem_pred_psi = aft.record.flux_linkage_fem
        fem_pred_torque = aft.record.torque_fem
        
        fem_tets = aft.record.mesh_data_fem.total_elements if hasattr(aft.record, 'mesh_data_fem') and aft.record.mesh_data_fem is not None else (i + 1)
        fem_tets_array.append(fem_tets)
        
        err_B_z = get_waveform_nrmse(data_true=fem_ref_B_z, data_pred=fem_pred_B_z, num_points=200, row_index=2)
        err_psi = get_waveform_nrmse(data_true=fem_ref_psi, data_pred=fem_pred_psi, num_points=200, row_index=2)
        err_torque = get_waveform_nrmse(data_true=fem_ref_torque, data_pred=fem_pred_torque, num_points=200, row_index=0)
        
        nrmse_fem_B_z.append(err_B_z)
        nrmse_fem_psi.append(err_psi)
        nrmse_fem_torque.append(err_torque)

    plt.figure(figsize=(fig_width, fig_height))
    plt.plot(fem_tets_array[:-1], nrmse_fem_B_z[:-1], color=s.colors[0], marker='o', linestyle='--', linewidth=2.5, markersize=9, label=r'FEM NRMSE of $B_z$')
    plt.plot(fem_tets_array[:-1], nrmse_fem_psi[:-1], color=s.colors[2], marker='s', linestyle='--', linewidth=2.5, markersize=9, label=r'FEM NRMSE of $\Psi_a$')
    plt.plot(fem_tets_array[:-1], nrmse_fem_torque[:-1], color=s.colors[1], marker='^', linestyle='--', linewidth=2.5, markersize=9, label='FEM NRMSE of Torque')
    plt.xlabel('Total FEM Tetrahedra Elements', fontsize=s.label_size)
    plt.ylabel('FEM Self-Convergence NRMSE (%)', fontsize=s.label_size)
    plt.title('3D-FEM Mesh Self-Convergence Rate Study', fontsize=s.title_size)
    plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
    plt.legend(frameon=True, loc='upper right', fontsize=s.legend_size)
    plt.tight_layout()
    plt.show()