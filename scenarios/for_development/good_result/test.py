import paths
import math
pi = math.pi
from types import SimpleNamespace

from src.core.storage.core import motor_io 
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1

# Option
reload_motor = False
file_name = "motor_test"

export_maxwell = True
show_geometry = False
solve_semiFEM = True

if reload_motor:
    aft = motor_io.load_motor(filename = file_name)

else:
    # 1. Init Object
    aft = AxialFluxMotorType1()

    # 2. Material Data
    aft.material_data.air = "default"
    aft.material_data.magnet_type = "NdFe30"
    aft.material_data.iron_type = "steel_1008"

    # 3. Winding Data
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
    stator.slot_number = 15
    stator.stator_lam_dia = 150 * 1e-3
    stator.stator_bore_dia = 70 * 1e-3
    stator.slot_opening = 2 * 1e-3
    stator.wdg_extension_inner = 0
    stator.wdg_extension_outer = 0
    stator.slot_width = 7 * 1e-3
    stator.slot_depth = 15 * 1e-3
    stator.slot_corner_radius = 0
    stator.tooth_tip_depth = 2 * 1e-3
    stator.tooth_tip_angle = 30
    stator.stator_length = 25 * 1e-3

    # 6. Khai báo Geometry Data - Rotor
    rotor = aft.geometry_data.rotor
    rotor.pole_number = 10
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

    calc.general_options.n_point = 20
    calc.general_options.solve_cogging = True
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
    mesh.n_r_2 = 3
    mesh.n_r_3 = 3
    mesh.n_r_out = 1
    mesh.n_theta = 150
    mesh.n_z_in_air = 1
    mesh.n_z_rotor_yoke = 3
    mesh.n_z_magnet = 3
    mesh.n_z_airgap = 3
    mesh.n_z_tooth_tip_1 = 3
    mesh.n_z_tooth_tip_2 = 3
    mesh.n_z_tooth_body = 3
    mesh.n_z_stator_yoke = 3
    mesh.n_z_out_air = 1 
    mesh.use_symmetry_factor = True
    mesh.periodic_boundary = True
    aft.just_changed("mesh")

    # 9. Khai báo Drive Data
    aft.drive_data.i_rms = 10.0
    aft.drive_data.phase_advanced = 0.0
    aft.just_changed("drive")

    # 10. Khai báo Maxwell Export Option
    aft.maxwell_export_option = SimpleNamespace(
            ansys_electronic_version = "2025.2",
            use_default_option = True,
            custom_option = SimpleNamespace(
                mesh_setting = SimpleNamespace(
                    band_mapping_angle = pi / 180,
                    maximum_element_length = 20 * 1e-3 # unit: m
                ),
                motion_setting = SimpleNamespace(
                    shaft_speed = 3000
                )
            ),
            current_function = None,
            solver_option = SimpleNamespace(
                solve_immediately = False,
                solve_only_1_step = False
            )
        )

if export_maxwell:
    aft.export_to_maxwell()

if show_geometry:
    aft.require("geometry")
    aft.geometry.show()

if solve_semiFEM:
    aft.analysis_motor()

    if reload_motor is False:
        motor_io.save_motor(motor_obj=aft,filename= file_name)

# Visualization
data_processor = aft.data_processor

data_processor.plot_flux_linkage(horizontal_axis="time")
data_processor.plot_back_emf(horizontal_axis="time")
data_processor.plot_back_emf_line(horizontal_axis="time")
data_processor.plot_current(horizontal_axis="time")
data_processor.plot_torque(horizontal_axis="time")
data_processor.plot_axial_force(horizontal_axis="time")
data_processor.plot_cogging_torque(horizontal_axis="time")
data_processor.plot_mechanical_power(horizontal_axis="time")
data_processor.plot_inductance_map()

data_processor.compare_flux_linkage(horizontal_axis="time")
data_processor.compare_back_emf(horizontal_axis="time")
data_processor.compare_back_emf_line(horizontal_axis="time")
data_processor.compare_torque(horizontal_axis="time")
data_processor.compare_mechanical_power(horizontal_axis="time")



#aft.display()





