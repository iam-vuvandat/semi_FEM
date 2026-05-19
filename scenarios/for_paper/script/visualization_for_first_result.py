import paths
import math
from src.core.storage.core.MotorIO import MotorIO
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
pi = math.pi
io = MotorIO()

# initial setup
from src.core.ansys_maxwell.rmxprt.setup.init_window import init_window
init_window()

file_name = "motor_for_paper" 
aft = io.load(path=file_name)
aft.calculation_data.general_options.solve_standard = True
aft.calculation_data.general_options.solve_cogging  = False
aft.calculation_data.general_options.solve_only_1_step = True

# Option
visualization_under_no_load = True
visualization_reluctance_network_first = False


if visualization_under_no_load:
    aft.drive_data.i_rms = 0.0
    aft.just_changed('drive_data')

refine_mesh = True
if refine_mesh:
    aft.adaptive_mesh_data.n_r_in = 1
    aft.adaptive_mesh_data.n_r_1 = 4
    aft.adaptive_mesh_data.n_r_2 = 12
    aft.adaptive_mesh_data.n_r_3 = 4
    aft.adaptive_mesh_data.n_r_out = 1
    aft.adaptive_mesh_data.n_theta = 180
    aft.adaptive_mesh_data.n_z_in_air = 1
    aft.adaptive_mesh_data.n_z_rotor_yoke = 6
    aft.adaptive_mesh_data.n_z_magnet = 3
    aft.adaptive_mesh_data.n_z_airgap = 5
    aft.adaptive_mesh_data.n_z_tooth_tip_1 = 2
    aft.adaptive_mesh_data.n_z_tooth_tip_2 = 6
    aft.adaptive_mesh_data.n_z_tooth_body = 10
    aft.adaptive_mesh_data.n_z_stator_yoke = 6
    aft.adaptive_mesh_data.n_z_out_air = 1
    aft.adaptive_mesh_data.use_symmetry_factor = True
    aft.adaptive_mesh_data.periodic_boundary = True
    aft.just_changed('mesh')


if visualization_reluctance_network_first:
    # Visualization for Reluctance Network
    aft.analysis_motor()
    aft.display()



# Visualization for FEM
aft.maxwell_export_option.solver_option.solve_only_1_step = True
aft.maxwell_export_option.solver_option.close_after_completed = False
aft.export_to_rmxprt()




if not visualization_reluctance_network_first:
    # Visualization for Reluctance Network
    aft.analysis_motor()
    aft.display()


print(aft.record.airgap_flux_density)
aft.data_processor.plot_airgap_flux_density()

