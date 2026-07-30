import paths
import numpy as np
import gc

from src.core.storage.core.MotorIO import MotorIO
from plot_mesh_elements_vs_config import plot_mesh_elements_vs_config

io = MotorIO()

re_create_motor = True
re_solve_3d_mbgrn = True
re_solve_fem = True
re_solve_index = []
re_plot = True
number_of_configuation = 7
original_file_name = "motor_for_paper"

file_name_array = [f"test_mesh{i}" for i in range(number_of_configuation)]
fem_element_lengths_mm = [5.50, 4.37, 3.81, 3.46, 3.22, 3.03, 2.88]

if isinstance(re_solve_index, int):
    target_indices = [re_solve_index]
elif isinstance(re_solve_index, (list, tuple)):
    target_indices = re_solve_index
else:
    target_indices = []

if re_create_motor:
    for i, file_name in enumerate(file_name_array):
        if target_indices and i not in target_indices:
            continue

        aft = io.load(path=original_file_name)
        aft.calculation_data.convergence_settings.max_iteration = 100
        aft.calculation_data.convergence_settings.max_relative_residual = 0.3 * 1e-2
        aft.calculation_data.convergence_settings.material_relax = 1.0
        aft.calculation_data.convergence_settings.damping_factor = 1.0
        aft.calculation_data.convergence_settings.relaxation_decay = 0.5
        aft.calculation_data.general_options.solve_cogging = False
        aft.calculation_data.general_options.solve_standard = True
        aft.calculation_data.general_options.solve_under_no_load = False
        aft.calculation_data.general_options.solve_on_load = True
        
        aft.calculation_data.general_options.solve_only_1_step = True
        aft.maxwell_export_option.solver_option.solve_only_1_step = True
        
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

        io.save(motor=aft, path=file_name)
        del aft
        gc.collect()

if re_solve_3d_mbgrn:
    for i, file_name in enumerate(file_name_array):
        if target_indices and i not in target_indices:
            continue
            
        aft = io.load(path=file_name)
        aft.analysis_motor()
        io.save(motor=aft, path=file_name)
        del aft
        gc.collect()

if re_solve_fem:
    for i, file_name in enumerate(file_name_array):
        if target_indices and i not in target_indices:
            continue
            
        aft = io.load(path=file_name)
        
        target_len = fem_element_lengths_mm[i]
        mesh_setting = aft.maxwell_export_option.custom_option.mesh_setting
        mesh_setting.length_band_element_length = target_len
        mesh_setting.length_coil_element_length = target_len
        mesh_setting.length_mag_element_length = target_len
        mesh_setting.length_main_element_length = target_len
        mesh_setting.length_region_element_length = target_len

        print(f"\033[94mSolving FEM Index {i} (Config Graph #{i+1}): Applied element length = {target_len:.2f} mm\033[0m")

        aft.export_to_rmxprt()

        io.save(motor=aft, path=file_name)
        del aft
        gc.collect()

if re_plot:
    plot_mesh_elements_vs_config(file_name_array, io)