import paths
from system.core import libraries_require
import time
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace 
from solver.utils.periodic_derivative import periodic_derivative
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import math
pi = math.pi


re_create_motor = False
re_solve = True

if not re_create_motor:
    aft = workspace.load("aft5")
    if re_solve:
        aft.reluctance_network.list_elements_lite = None
else:
    aft = AxialFluxMotorType1(magnet_length=3.0 * 1e-3, airgap=1.0 * 1e-3)
    aft.create_geometry()

    aft.create_adaptive_mesh(n_r_in              =2,
                         n_r_1                   =3,
                         n_r_2                   =4,
                         n_r_3                   =3,
                         n_r_out                 =2,
                         n_theta                 =80,
                         n_z_in_air              =2,
                         n_z_rotor_yoke          =4,
                         n_z_magnet              =3,
                         n_z_airgap              =3,
                         n_z_tooth_tip_1         =2,
                         n_z_tooth_tip_2         =3,
                         n_z_tooth_body          =5,
                         n_z_stator_yoke         =3,
                         n_z_out_air             =2,
                         use_symmetry_factor=True,
                         periodic_boundary=True)
    
    aft.create_reluctance_network()
    aft.reluctance_network.update_reluctance_network(magnetic_potential=aft.reluctance_network.magnetic_potential)
    workspace.save(aft5=aft)

if re_solve:
    start_time = time.perf_counter()
    n_theta = aft.mesh.detail_parameter[5] - 1 
    n_step_shift = 5
    n_step_solve = int(n_theta // n_step_shift)

    flux_linkage = np.zeros((4, n_step_solve))

    for i in tqdm(range(1), desc="Solving & Rotating"):
        aft.reluctance_network.solve_magnetic_equation(debug = True)
        aft.rotate_rotor(n_step=n_step_shift)
aft.reluctance_network.show()