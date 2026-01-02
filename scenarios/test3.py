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

from solver.utils.newton_raphson import newton_raphson_iteration
from solver.utils.fixed_point_iteration import fix_point_iteration
from solver.utils.fixed_point_at_peak import fixed_point_at_peak

re_create_motor = False
re_solve = True

if not re_create_motor:
    aft = workspace.load("aft7")
    if re_solve:
        aft.reluctance_network.list_elements_lite = None
else:
    aft = AxialFluxMotorType1(magnet_length= 3 * 1e-3,
                              airgap=1.5 * 1e-3,
                              stator_length = 25* 1e-3,
                              rotor_length = 7 * 1e-3)
    aft.create_geometry()

    aft.create_adaptive_mesh(n_r_in              =2,
                         n_r_1                   =3,
                         n_r_2                   =5,
                         n_r_3                   =3,
                         n_r_out                 =2,
                         n_theta                 =75,
                         n_z_in_air              =2,
                         n_z_rotor_yoke          =3,
                         n_z_magnet              =3,
                         n_z_airgap              =3,
                         n_z_tooth_tip_1         =3,
                         n_z_tooth_tip_2         =3,
                         n_z_tooth_body          =5,
                         n_z_stator_yoke         =3,
                         n_z_out_air             =2,
                         use_symmetry_factor=True,
                         periodic_boundary=True)
    
    aft.create_reluctance_network()
    aft.reluctance_network.update_reluctance_network(magnetic_potential=aft.reluctance_network.magnetic_potential)
    workspace.save(aft7=aft)

if re_solve:
    start_time = time.perf_counter()
    n_theta = aft.mesh.detail_parameter[5] - 1 
    n_step_shift = 5
    n_step_solve = int(n_theta // n_step_shift)

    flux_linkage = np.zeros((4, n_step_solve))

    for i in tqdm(range(1), desc="Solving & Rotating"):
        aft.reluctance_network.material_database.reset()
        aft.reluctance_network.nonlinear_conjugate_gradient()
                                                      
        aft.rotate_rotor(n_step=n_step_shift)
        
        data_out = aft.reluctance_network.get_flux_linkage().flux_linkage
        flux_linkage[:, i] = data_out.flatten()


    end_time = time.perf_counter()
    total_time = end_time - start_time #s
    total_time *= 1/60 # minute
    print("total time = ",total_time," minute")

    aft.record.flux_linkage = flux_linkage
    shaft_speed = aft.shaft_speed #rpm
    shaft_speed *= 2*pi / 60 # rad/s
    aft.record.back_emf_phase = periodic_derivative(data=flux_linkage).derivative * shaft_speed
    
    workspace.save(aft7=aft)
     


aft.reluctance_network.show()