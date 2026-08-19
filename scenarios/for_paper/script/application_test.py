import paths
import math
from src.core.storage.core.MotorIO import MotorIO
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
pi = math.pi
io = MotorIO()

from src.core.ansys_maxwell.rmxprt.setup.init_window import init_window
init_window()

# option
reload_motor = True
file_name = "motor_for_paper" 
solveFEM = False
solveMBGRN = False

# suboption
solve_cogging = True
sovle_standard = True
solve_under_no_load = True
solve_on_load = True
solve_only_1_step = False

if reload_motor:
    aft = io.load(path=file_name)
else:
    aft1 = io.load(path=file_name)
    aft = AxialFluxMotorType1()
    aft.record = aft1.record

    aft.winding_data.turns = 20
    aft.winding_data.throw = 1
    aft.just_changed('winding_data')

    aft.mechanical_data.shaft_speed = 3000
    aft.just_changed('mechanical_data')

    aft.geometry_data.stator.slot_number = 30
    aft.geometry_data.stator.stator_lam_dia = 150 * 1e-3
    aft.geometry_data.stator.stator_bore_dia = 70 * 1e-3
    aft.geometry_data.stator.slot_opening = 2 * 1e-3
    aft.geometry_data.stator.wdg_extension_inner = 0
    aft.geometry_data.stator.wdg_extension_outer = 0
    aft.geometry_data.stator.slot_width = 5 * 1e-3
    aft.geometry_data.stator.slot_depth = 15 * 1e-3
    aft.geometry_data.stator.slot_corner_radius = 0
    aft.geometry_data.stator.tooth_tip_depth = 2 * 1e-3
    aft.geometry_data.stator.tooth_tip_angle = 30
    aft.geometry_data.stator.stator_length = 25 * 1e-3
    
    aft.geometry_data.rotor.pole_number = 20
    aft.geometry_data.rotor.rotor_lam_dia = 150 * 1e-3
    aft.geometry_data.rotor.magnet_arc = 160
    aft.geometry_data.rotor.magnet_embed_depth = 5 * 1e-3
    aft.geometry_data.rotor.magnet_depth = 30 * 1e-3
    aft.geometry_data.rotor.magnet_segments = 1
    aft.geometry_data.rotor.banding_depth = 0 * 1e-3
    aft.geometry_data.rotor.shaft_dia = 0 * 1e-3
    aft.geometry_data.rotor.shaft_hole_diameter = 70 * 1e-3
    aft.geometry_data.rotor.airgap = 1.5 * 1e-3
    aft.geometry_data.rotor.magnet_length = 3 * 1e-3
    aft.geometry_data.rotor.rotor_length = 6 * 1e-3

    aft.just_changed('geometry_data')

    aft.calculation_data.convergence_settings.max_iteration = 100
    aft.calculation_data.convergence_settings.max_relative_residual = 0.3 * 1e-2
    aft.calculation_data.convergence_settings.material_relax = 1.0
    aft.calculation_data.convergence_settings.damping_factor = 1.0
    aft.calculation_data.convergence_settings.relaxation_decay = 0.5

    aft.calculation_data.general_options.n_point = 30
    aft.calculation_data.general_options.solve_cogging = solve_cogging
    aft.calculation_data.general_options.solve_standard = sovle_standard
    aft.calculation_data.general_options.solve_under_no_load = solve_under_no_load
    aft.calculation_data.general_options.solve_on_load = solve_on_load
    aft.calculation_data.general_options.solve_only_1_step = solve_only_1_step
    
    aft.calculation_data.export_inductance_options.export_inductance = False
    aft.calculation_data.export_inductance_options.current_min = 1.0
    aft.calculation_data.export_inductance_options.current_max = 15.0
    aft.calculation_data.export_inductance_options.current_resolution = 10
    aft.just_changed('calculation_data')

    

    aft.adaptive_mesh_data.n_r_1 = 9
    aft.adaptive_mesh_data.n_r_2 = 9
    aft.adaptive_mesh_data.n_r_3 = 9
    aft.adaptive_mesh_data.n_z_rotor_yoke = 9
    aft.adaptive_mesh_data.n_z_magnet = 9
    aft.adaptive_mesh_data.n_z_airgap = 11
    aft.adaptive_mesh_data.n_z_tooth_tip_1 = 9
    aft.adaptive_mesh_data.n_z_tooth_tip_2 = 9
    aft.adaptive_mesh_data.n_z_tooth_body = 9
    aft.adaptive_mesh_data.n_z_stator_yoke = 9
    aft.just_changed('mesh')

    aft.drive_data.i_rms = 10.0
    aft.drive_data.phase_advanced = 0.0
    aft.just_changed('drive')
    
    aft.maxwell_export_option.ansys_electronic_version = "2025.2"
    aft.maxwell_export_option.use_default_option = True

    aft.maxwell_export_option.custom_option.mesh_setting.cylindrical_gap_1.clone_mesh = False
    
    target_len = 2.3
    mesh_setting = aft.maxwell_export_option.custom_option.mesh_setting
    mesh_setting.length_band_element_length = target_len
    mesh_setting.length_coil_element_length = target_len
    mesh_setting.length_mag_element_length = target_len
    mesh_setting.length_main_element_length = target_len
    mesh_setting.length_region_element_length = target_len

    aft.maxwell_export_option.custom_option.motion_setting.shaft_speed = 3000

    aft.maxwell_export_option.solver_option.alternetive_first_point = True
    aft.maxwell_export_option.solver_option.solve_immediately = True
    aft.maxwell_export_option.solver_option.solve_only_1_step = solve_only_1_step
    aft.maxwell_export_option.solver_option.close_after_completed = False

    if solveFEM:
        aft.export_to_rmxprt()
    if solveMBGRN:
        aft.analysis_motor()
    io.save(motor=aft, path=file_name)

aft.display()

dp = aft.data_processor

dp.plot_airgap_flux_density(plot=False)
dp.plot_airgap_flux_density_no_load(plot=False)
dp.plot_flux_linkage(horizontal_axis="time", show_fem=True, show_dq=False, show_all_phase=True, plot=False)
dp.plot_flux_linkage_no_load(horizontal_axis="time", show_fem=True, show_dq=False, show_all_phase=True, plot=False)
dp.plot_back_emf(horizontal_axis="time", show_fem=True, show_all_phases=True, plot=False)
dp.plot_back_emf_no_load(horizontal_axis="time", show_fem=True, show_all_phases=True, plot=False)
dp.plot_torque(horizontal_axis="time", show_fem=True, plot=False)
dp.plot_mechanical_power(horizontal_axis="time", show_fem=True, plot=False)
dp.plot_cogging_torque(horizontal_axis="time", show_fem=True, revert=False, num_periods=5, plot=False)
dp.plot_axial_force(horizontal_axis="time", show_fem=True, plot=False)
dp.plot_axial_force_no_load(horizontal_axis="time", show_fem=True, plot=False)
dp.plot_current(plot=False)
dp.create_report()

