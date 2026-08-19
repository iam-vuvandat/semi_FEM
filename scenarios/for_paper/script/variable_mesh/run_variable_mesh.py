import os
import paths
import numpy as np
import gc

from src.core.ansys_maxwell.rmxprt.setup.init_window import init_window
init_window()
from src.core.storage.core.MotorIO import MotorIO

from plot_mesh_elements_vs_config import plot_mesh_elements_vs_config
from plot_fem_torque import plot_fem_torque
from plot_fem_cogging_torque import plot_fem_cogging_torque
from plot_fem_flux_linkage import plot_fem_flux_linkage
from plot_fem_airgap_flux_density_bz import plot_fem_airgap_flux_density_bz
from plot_fem_self_convergence import plot_fem_self_convergence
from plot_mbgrn_torque import plot_mbgrn_torque
from plot_mbgrn_cogging_torque import plot_mbgrn_cogging_torque
from plot_mbgrn_flux_linkage import plot_mbgrn_flux_linkage
from plot_mbgrn_airgap_flux_density import plot_mbgrn_airgap_flux_density
from plot_mbgrn_self_convergence import plot_mbgrn_self_convergence

io = MotorIO()

current_script_dir = os.path.dirname(os.path.abspath(__file__))
figures_dir = os.path.join(current_script_dir, "figures")
os.makedirs(figures_dir, exist_ok=True)

data_dir = os.path.join(current_script_dir, "data")
os.makedirs(data_dir, exist_ok=True)

re_create_motor = False
re_solve_3d_mbgrn = False
re_solve_fem = False
re_solve_index = []
re_plot = True
number_of_configuation = 9
original_file_name_base = "motor_for_paper"
original_file_path = os.path.join(data_dir, original_file_name_base)
file_path_array = [os.path.join(data_dir, f"variable_mesh{i}") for i in range(number_of_configuation)]
fem_element_lengths_mm = [5.50, 4.30, 3.60, 3.10, 2.95, 2.8, 2.5, 2.4, 2.3]
selected_mesh_indices = [0,1,2,3,4,5,6,7,8]

if isinstance(re_solve_index, int):
    target_indices = [re_solve_index]
elif isinstance(re_solve_index, (list, tuple)):
    target_indices = re_solve_index
else:
    target_indices = []

if re_create_motor:
    for i, file_path in enumerate(file_path_array):
        if target_indices and i not in target_indices:
            continue

        try:
            aft = io.load(path=file_path)
        except Exception:
            aft = io.load(path=original_file_name_base)

        aft.calculation_data.convergence_settings.max_iteration = 100
        aft.calculation_data.convergence_settings.max_relative_residual = 0.3 * 1e-2
        aft.calculation_data.convergence_settings.material_relax = 1.0
        aft.calculation_data.convergence_settings.damping_factor = 1.0
        aft.calculation_data.convergence_settings.relaxation_decay = 0.5
        aft.calculation_data.general_options.solve_cogging = True
        aft.calculation_data.general_options.solve_standard = True
        aft.calculation_data.general_options.solve_under_no_load = False
        aft.calculation_data.general_options.solve_on_load = True
        aft.calculation_data.general_options.solve_only_1_step = False
        aft.maxwell_export_option.solver_option.solve_only_1_step = False
        aft.calculation_data.general_options.n_point = 30
        aft.just_changed('calculation_data')

        aft.adaptive_mesh_data.n_r_1 = 1 + i
        aft.adaptive_mesh_data.n_r_2 = 1 + i
        aft.adaptive_mesh_data.n_r_3 = 1 + i 
        aft.adaptive_mesh_data.n_z_rotor_yoke = 1 + i
        aft.adaptive_mesh_data.n_z_magnet = 1 + i
        aft.adaptive_mesh_data.n_z_airgap = 3 + i
        aft.adaptive_mesh_data.n_z_tooth_tip_1 = 1 + i
        aft.adaptive_mesh_data.n_z_tooth_tip_2 = 1 + i 
        aft.adaptive_mesh_data.n_z_tooth_body = 1 + i
        aft.adaptive_mesh_data.n_z_stator_yoke = 1 + i
        aft.just_changed('mesh')
        aft.update_mesh_by_calculation_data()

        if i != number_of_configuation - 1:
            aft.maxwell_export_option.solver_option.close_after_completed = True
        else:
            aft.maxwell_export_option.solver_option.close_after_completed = False

        aft.maxwell_export_option.custom_option.mesh_setting.cylindrical_gap_1.clone_mesh = False

        target_len = fem_element_lengths_mm[i]
        mesh_setting = aft.maxwell_export_option.custom_option.mesh_setting
        mesh_setting.length_band_element_length = target_len
        mesh_setting.length_coil_element_length = target_len
        mesh_setting.length_mag_element_length = target_len
        mesh_setting.length_main_element_length = target_len
        mesh_setting.length_region_element_length = target_len

        io.save(motor=aft, path=file_path)
        del aft
        gc.collect()

if re_solve_3d_mbgrn:
    for i, file_path in enumerate(file_path_array):
        if target_indices and i not in target_indices:
            continue

        aft = io.load(path=file_path)
        aft.analysis_motor()
        io.save(motor=aft, path=file_path)
        del aft
        gc.collect()

if re_solve_fem:
    for i, file_path in enumerate(file_path_array):
        if target_indices and i not in target_indices:
            continue

        aft = io.load(path=file_path)
        
        target_len = fem_element_lengths_mm[i]
        mesh_setting = aft.maxwell_export_option.custom_option.mesh_setting
        mesh_setting.length_band_element_length = target_len
        mesh_setting.length_coil_element_length = target_len
        mesh_setting.length_mag_element_length = target_len
        mesh_setting.length_main_element_length = target_len
        mesh_setting.length_region_element_length = target_len

        print(f"\033[94mSolving FEM Index {i} (Config Graph #{i+1}): Applied element length = {target_len:.2f} mm\033[0m")

        aft.export_to_rmxprt()

        io.save(motor=aft, path=file_path)
        del aft
        gc.collect()

if re_plot:
    print("\n\033[92m---> Running Post-Processing Plot Functions...\033[0m")
    plot_mesh_elements_vs_config(file_path_array, io, figures_dir=figures_dir)
    
    plot_fem_torque(file_path_array, io, figures_dir=figures_dir, mesh_indices=selected_mesh_indices)
    plot_fem_cogging_torque(file_path_array, io, figures_dir=figures_dir, mesh_indices=selected_mesh_indices)
    plot_fem_flux_linkage(file_path_array, io, figures_dir=figures_dir, mesh_indices=selected_mesh_indices)
    plot_fem_airgap_flux_density_bz(file_path_array, io, figures_dir=figures_dir, mesh_indices=selected_mesh_indices)
    plot_mbgrn_torque(file_path_array, io, figures_dir=figures_dir, mesh_indices=selected_mesh_indices)
    plot_mbgrn_cogging_torque(file_path_array, io, figures_dir=figures_dir, mesh_indices=selected_mesh_indices)
    plot_mbgrn_flux_linkage(file_path_array, io, figures_dir=figures_dir, mesh_indices=selected_mesh_indices)
    plot_mbgrn_airgap_flux_density(file_path_array, io, figures_dir=figures_dir, mesh_indices=selected_mesh_indices)
    
    plot_fem_self_convergence(file_path_array, io, figures_dir=figures_dir)
    plot_mbgrn_self_convergence(file_path_array, io, figures_dir=figures_dir)
    
    print(f"\033[92m---> All plots generated successfully and saved to: {figures_dir}\033[0m\n")