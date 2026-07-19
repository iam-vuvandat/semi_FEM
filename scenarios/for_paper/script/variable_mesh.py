import paths
import numpy as np
import matplotlib.pyplot as plt
import gc

from src.core.storage.core.MotorIO import MotorIO
io = MotorIO()
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style

s = apply_journal_style()
fig_width = 10
fig_height = fig_width / 1.5

re_solve = True
file_name = "motor_for_paper"
number_of_configuation = 10

file_name_array = []
for i in range(number_of_configuation):
    new_file_name = f"motor_for_paper{i}"
    file_name_array.append(new_file_name)
print(f"\033[94m{file_name_array}\033[0m")

if re_solve:
    for i in range(number_of_configuation):
        aft = io.load(path=file_name)
        
        aft.calculation_data.convergence_settings.max_iteration = 100
        aft.calculation_data.convergence_settings.max_relative_residual = 0.5 * 1e-2
        aft.calculation_data.convergence_settings.material_relax = 1.0
        aft.calculation_data.convergence_settings.damping_factor = 1.0
        aft.calculation_data.convergence_settings.relaxation_decay = 0.5

        aft.calculation_data.general_options.solve_cogging = False
        aft.calculation_data.general_options.solve_standard = True
        aft.calculation_data.general_options.solve_under_no_load = False
        aft.calculation_data.general_options.solve_on_load = True

        aft.just_changed('calculation_data')
        
        aft.calculation_data.general_options.n_point = 16 + i * 8
        aft.just_changed('calculation_data')
        
        aft.adaptive_mesh_data.n_r_1 = 1 + i
        aft.adaptive_mesh_data.n_r_2 = 1 + i
        aft.adaptive_mesh_data.n_r_3 = 1 + i

        aft.adaptive_mesh_data.n_z_rotor_yoke = 2 + i
        aft.adaptive_mesh_data.n_z_magnet = 2 + i
        aft.adaptive_mesh_data.n_z_airgap = 3 + i * 2
        aft.adaptive_mesh_data.n_z_tooth_tip_1 = 1 + i
        aft.adaptive_mesh_data.n_z_tooth_tip_2 = 3 + i 
        aft.adaptive_mesh_data.n_z_tooth_body = 3 + i
        aft.adaptive_mesh_data.n_z_stator_yoke = 2 + i
        
        aft.just_changed('mesh')
        aft.update_mesh_by_calculation_data()
        
        aft.analysis_motor()
        io.save(motor=aft, path=file_name_array[i])
        
        del aft
        gc.collect()

    motor_array = []
    for i in range(number_of_configuation):
        aft = io.load(path=file_name_array[i])
        motor_array.append(aft)

    table_data = []
    for idx, aft in enumerate(motor_array):
        aft.require('mesh')
        table_data.append((idx, aft.mesh.n_cells_r, aft.mesh.n_cells_t, aft.mesh.n_cells_z, aft.mesh.total_cells))

    print(f"{'Config':<8} | {'n_cells_r':<10} | {'n_cells_t':<10} | {'n_cells_z':<10} | {'total_cells':<12}")
    print("-" * 62)
    for row in table_data:
        print(f"{row[0]:<8} | {row[1]:<10} | {row[2]:<10} | {row[3]:<10} | {row[4]:<12}")

    config_index = [row[0] + 1 for row in table_data]
    total_elements = [row[4] for row in table_data]

    plt.figure(figsize=(fig_width, fig_height))
    plt.plot(config_index, total_elements, marker='o', color=s.colors[0], linewidth=2.0, markersize=8)
    plt.xlabel('Mesh Configuration Index', fontsize=s.label_size)
    plt.ylabel('Total Mesh Cells', fontsize=s.label_size)
    plt.title('Total Mesh Cells vs Configuration Index', fontsize=s.title_size)
    plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
    plt.tight_layout()
    plt.show()

else: 
    motor_array = []
    for i in range(number_of_configuation):
        aft = io.load(path=file_name_array[i])
        motor_array.append(aft)


# Overlay Axial Airgap Flux Density
    plt.figure(figsize=(fig_width, fig_height))
    
    for i, aft in enumerate(motor_array):
        aft.require('mesh')
        
        record = aft.record
        x_axis = record.airgap_flux_density[4, :]
        B_z = record.airgap_flux_density[2, :]
        total_cells = aft.mesh.total_cells
        
        lw = 2.8 if i == number_of_configuation - 1 else 1.8
        
        plt.plot(
            x_axis, 
            B_z, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(x_axis) // 25),
            markersize=7,
            linewidth=lw, 
            label=f"Mesh {i+1} ({total_cells:,} cells)"
        )
        
    plt.xlabel('Angular Position (rad)', fontsize=s.label_size)
    plt.ylabel('Airgap Flux Density $B_z$ (T)', fontsize=s.label_size)
    plt.title('Airgap Axial Flux Density ($B_z$) Convergence Study', fontsize=s.title_size)
    plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
    plt.legend(frameon=True, loc='upper right', ncol=2, fontsize=s.legend_size)
    plt.margins(x=0)
    plt.tight_layout()
    plt.show()

# Overlay Flux Linkage On-Load
    plt.figure(figsize=(fig_width, fig_height))
    
    for i, aft in enumerate(motor_array):
        aft.require('mesh')
        
        record = aft.record
        shaft_speed = (aft.mechanical_data.shaft_speed * np.pi * 2) / 60
        
        theta_data = record.flux_linkage[-1, :]
        time_ms = (theta_data / shaft_speed) * 1e3
        psi_a = record.flux_linkage[2, :]
        total_cells = aft.mesh.total_cells
        
        lw = 2.8 if i == number_of_configuation - 1 else 1.8
        
        plt.plot(
            time_ms, 
            psi_a, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(time_ms) // 25),
            markersize=7,
            linewidth=lw, 
            label=f"Mesh {i+1} ({total_cells:,} cells)"
        )
        
    plt.xlabel('Time (ms)', fontsize=s.label_size)
    plt.ylabel('Flux Linkage $\Psi_a$ (Wb)', fontsize=s.label_size)
    plt.title('Phase A On-Load Flux Linkage Convergence Study', fontsize=s.title_size)
    plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
    plt.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
    plt.margins(x=0)
    plt.tight_layout()
    plt.show()

# Overlay Torque On-Load
    plt.figure(figsize=(fig_width, fig_height))
    
    for i, aft in enumerate(motor_array):
        aft.require('mesh')
        
        record = aft.record
        shaft_speed = (aft.mechanical_data.shaft_speed * np.pi * 2) / 60
        
        theta_data = record.torque[-1, :]
        time_ms = (theta_data / shaft_speed) * 1e3
        val_torque = record.torque[0, :]
        total_cells = aft.mesh.total_cells
        
        lw = 2.8 if i == number_of_configuation - 1 else 1.8
        
        plt.plot(
            time_ms, 
            val_torque, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(time_ms) // 25),
            markersize=7,
            linewidth=lw, 
            label=f"Mesh {i+1} ({total_cells:,} cells)"
        )
        
    plt.xlabel('Time (ms)', fontsize=s.label_size)
    plt.ylabel('Torque (Nm)', fontsize=s.label_size)
    plt.title('On-Load Electromagnetic Torque Convergence Study', fontsize=s.title_size)
    plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
    plt.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
    plt.margins(x=0)
    plt.tight_layout()
    plt.show()

# Overlay Evaluation Table and Mesh Convergence Errors
    reference_aft = motor_array[-1]
    reference_aft.require('mesh')
    
    data_true_B_z = reference_aft.record.airgap_flux_density
    data_true_psi = reference_aft.record.flux_linkage
    data_true_torque = reference_aft.record.torque
    
    mesh_indices = []
    total_elements = []
    cpu_times = []
    memory_usages = []
    
    nrmse_B_z = []
    nrmse_psi = []
    nrmse_torque = []
    
    for i in range(number_of_configuation):
        aft = motor_array[i]
        aft.require('mesh')
        
        mesh_indices.append(i + 1)
        total_elements.append(aft.record.elements)
        cpu_times.append(aft.record.time_solved)
        memory_usages.append(aft.record.memory_used)
        
        data_pred_B_z = aft.record.airgap_flux_density
        data_pred_psi = aft.record.flux_linkage
        data_pred_torque = aft.record.torque
        
        err_B_z = get_waveform_nrmse(data_true=data_true_B_z, data_pred=data_pred_B_z, num_points=200, row_index=2)
        err_psi = get_waveform_nrmse(data_true=data_true_psi, data_pred=data_pred_psi, num_points=200, row_index=2)
        err_torque = get_waveform_nrmse(data_true=data_true_torque, data_pred=data_pred_torque, num_points=200, row_index=0)
        
        nrmse_B_z.append(err_B_z)
        nrmse_psi.append(err_psi)
        nrmse_torque.append(err_torque)
        
    print(f"\n{'Mesh':<6} | {'Elements':<10} | {'Memory (MB)':<12} | {'CPU Time (s)':<14} | {'NRMSE Bz (%)':<14} | {'NRMSE Psi (%)':<15} | {'NRMSE Torque (%)':<16}")
    print("-" * 104)
    for idx in range(number_of_configuation):
        print(f"Mesh {mesh_indices[idx]:<1} | {total_elements[idx]:<10,} | {memory_usages[idx]:<12.2f} | {cpu_times[idx]:<14.4f} | {nrmse_B_z[idx]:<14.4f} | {nrmse_psi[idx]:<15.4f} | {nrmse_torque[idx]:<16.4f}")

    plt.figure(figsize=(fig_width, fig_height))
    
    plt.plot(total_elements[:-1], nrmse_B_z[:-1], color=s.colors[0], marker='o', linestyle='-', linewidth=2.5, markersize=9, label=r'NRMSE of $B_z$')
    plt.plot(total_elements[:-1], nrmse_psi[:-1], color=s.colors[2], marker='s', linestyle='-', linewidth=2.5, markersize=9, label=r'NRMSE of $\Psi_a$')
    plt.plot(total_elements[:-1], nrmse_torque[:-1], color=s.colors[1], marker='^', linestyle='-', linewidth=2.5, markersize=9, label='NRMSE of Torque')
    
    plt.xlabel('Total Mesh Elements ($Q_E$)', fontsize=s.label_size)
    plt.ylabel('Normalized RMSE (%)', fontsize=s.label_size)
    plt.title('Electromagnetic Variables Convergence Trend Analysis', fontsize=s.title_size)
    plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
    plt.legend(frameon=True, loc='upper right', fontsize=s.legend_size)
    plt.tight_layout()
    plt.show()

# Overlay Print Bz Data for All Motors
    for idx, aft in enumerate(motor_array):
        aft.require('mesh')
        record = aft.record
        B_z_array = record.airgap_flux_density[2, :]
        total_cells = aft.mesh.total_cells
        
        print(f"\n==================================================")
        print(f"Mesh {idx + 1} ({total_cells:,} cells) - Axial Airgap Flux Density B_z (T)")
        print(f"Total data points: {len(B_z_array)}")
        print(f"==================================================")
        print(B_z_array)