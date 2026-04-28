import paths
import math
from types import SimpleNamespace
from src.core.storage.core.MotorIO import MotorIO
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
pi = math.pi
io = MotorIO()

aft = AxialFluxMotorType1()
aft.adaptive_mesh_data = SimpleNamespace(
    n_r_in          = 1,
    n_r_1           = 3,
    n_r_2           = 10,
    n_r_3           = 3,
    n_r_out         = 1,
    n_theta         = 40,
    n_z_in_air      = 1,
    n_z_rotor_yoke  = 1,
    n_z_magnet      = 1,
    n_z_airgap      = 1,
    n_z_tooth_tip_1 = 1,
    n_z_tooth_tip_2 = 6,
    n_z_tooth_body  = 10,
    n_z_stator_yoke = 1,
    n_z_out_air     = 1,
    use_symmetry_factor = True,
    periodic_boundary   = True
)

aft.calculation_data.general_options.n_point = 40
aft.calculation_data.solve_only_1_step = True
aft.calculation_data.solve_cogging  = False

aft.just_changed('calculation_data')

aft.analysis_motor()
aft.display()