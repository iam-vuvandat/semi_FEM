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
    n_r_1           = 1,
    n_r_2           = 2,
    n_r_3           = 1,
    n_r_out         = 1,
    n_theta         = 40,
    n_z_in_air      = 1,
    n_z_rotor_yoke  = 2,
    n_z_magnet      = 1,
    n_z_airgap      = 1,
    n_z_tooth_tip_1 = 1,
    n_z_tooth_tip_2 = 1,
    n_z_tooth_body  = 3,
    n_z_stator_yoke = 2,
    n_z_out_air     = 1,
    use_symmetry_factor = True,
    periodic_boundary   = True
)
aft.display()