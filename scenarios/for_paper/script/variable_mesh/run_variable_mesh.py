import paths
import numpy as np
import gc

from src.core.storage.core.MotorIO import MotorIO
io = MotorIO()

# Execution flags and parameters
re_create_motor = True
re_solve_3d_mbgrn = True
re_solve_fem = True
number_of_configuation = 5

file_name_array = [f"motor_for_paper{i}" for i in range(number_of_configuation)]

# -------------------------------------------------------------------------
# STEP 1: INITIAL CONFIGURATION
# -------------------------------------------------------------------------
if re_create_motor:
    for i, file_name in enumerate(file_name_array):
        aft = io.load(path=file_name)

        # Set 3D-MBGRN solver parameters
        aft.calculation_data.convergence_settings.max_iteration = 100
        aft.calculation_data.convergence_settings.max_relative_residual = 0.3 * 1e-2
        aft.calculation_data.convergence_settings.material_relax = 1.0
        aft.calculation_data.convergence_settings.damping_factor = 1.0
        aft.calculation_data.convergence_settings.relaxation_decay = 0.5
        aft.calculation_data.general_options.solve_cogging = False
        aft.calculation_data.general_options.solve_standard = True
        aft.calculation_data.general_options.solve_under_no_load = False
        aft.calculation_data.general_options.solve_on_load = True
        aft.calculation_data.general_options.n_point = 30
        aft.just_changed('calculation_data')

        # Set 3D-MBGRN mesh refinement steps
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

        # Manage Maxwell instance lifecycle
        if i != number_of_configuation - 1:
            aft.maxwell_export_option.solver_option.close_after_completed = True
        else:
            aft.maxwell_export_option.solver_option.close_after_completed = False

        aft.maxwell_export_option.custom_option.mesh_setting.cylindrical_gap_1.clone_mesh = False

        # Set -1 for all regions at step 0 to use default Maxwell mesh
        mesh_setting = aft.maxwell_export_option.custom_option.mesh_setting
        if i == 0:
            mesh_setting.length_band_element_length = -1
            mesh_setting.length_coil_element_length = -1
            mesh_setting.length_mag_element_length = -1
            mesh_setting.length_main_element_length = -1
            mesh_setting.length_region_element_length = -1

        io.save(motor=aft, path=file_name)
        del aft
        gc.collect()

# -------------------------------------------------------------------------
# STEP 2: SOLVE MODELS & APPLY MESH REFINEMENT
# -------------------------------------------------------------------------

# 2A. Solve 3D-MBGRN for all configurations
if re_solve_3d_mbgrn:
    for i, file_name in enumerate(file_name_array):
        aft = io.load(path=file_name)
        aft.analysis_motor()
        io.save(motor=aft, path=file_name)
        del aft
        gc.collect()

# 2B. Solve 3D-FEM with progressive mesh refinement
if re_solve_fem:
    # Run step 0 to obtain default baseline max element length (in mm)
    aft_0 = io.load(path=file_name_array[0])
    aft_0.export_to_rmxprt()
    
    default_max_len_mm = aft_0.record.mesh_data_fem.max_element_length
    print(f"\033[92mStep 0 Completed: Baseline FEM max element length = {default_max_len_mm:.2f} mm\033[0m")
    
    io.save(motor=aft_0, path=file_name_array[0])
    del aft_0
    gc.collect()

    # Apply scaled max element length (in mm) for subsequent steps (i > 0)
    for i in range(1, number_of_configuation):
        file_name = file_name_array[i]
        aft = io.load(path=file_name)

        # Linearly reduce max element length based on step 0 baseline
        reduction_factor = 1.0 - (i / number_of_configuation)
        target_max_len_mm = default_max_len_mm * reduction_factor

        # Assign reduced element length to all 5 mesh regions
        mesh_setting = aft.maxwell_export_option.custom_option.mesh_setting
        mesh_setting.length_band_element_length = target_max_len_mm
        mesh_setting.length_coil_element_length = target_max_len_mm
        mesh_setting.length_mag_element_length = target_max_len_mm
        mesh_setting.length_main_element_length = target_max_len_mm
        mesh_setting.length_region_element_length = target_max_len_mm

        print(f"\033[94mStep {i}: Applied FEM regional element length = {target_max_len_mm:.2f} mm\033[0m")

        # Run Maxwell FEM simulation
        aft.export_to_rmxprt()

        io.save(motor=aft, path=file_name)
        del aft
        gc.collect()