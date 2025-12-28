import paths
from system.core import libraries_require
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace 
from tqdm import tqdm

re_create_motor = False
re_solve = False

if re_create_motor == False:
    print("loading aft")
    aft = workspace.load("aft2")
    print("load aft successfully")
    if re_solve == False:
        pass
    else:
        aft.reluctance_network.list_elements_lite = None
else:
    aft = AxialFluxMotorType1(magnet_length=4.0 * 1e-3,
                              airgap=0.5 * 1e-3)
    aft.create_geometry()
    aft.create_adaptive_mesh(n_r_in                       =2,
                         n_r_1                        =3,
                         n_r_2                        =6,
                         n_r_3                        =6,
                         n_r_out                      =2,
                         n_theta                      =120,
                         n_z_in_air                   =2,
                         n_z_rotor_yoke               =6,
                         n_z_magnet                   =5,
                         n_z_airgap                   =4,
                         n_z_tooth_tip_1              =3,
                         n_z_tooth_tip_2              =5,
                         n_z_tooth_body               =10,
                         n_z_stator_yoke              =6,
                         n_z_out_air                  =2,
                         use_symmetry_factor=True,
                         periodic_boundary=True)
    aft.create_reluctance_network()
    aft.reluctance_network.update_reluctance_network(magnetic_potential=aft.reluctance_network.magnetic_potential)
    workspace.save(aft2=aft)

if re_solve == True:
    n_theta = aft.mesh.detail_parameter[5] - 1 
    n_step_shift = 2
    n_step_solve = n_theta // n_step_shift

    for i in tqdm(range(int(n_step_solve)), desc="Solving & Rotating"):
        aft.reluctance_network.solve_magnetic_equation()
        aft.rotate_rotor(n_step=n_step_shift)

    workspace.save(aft2=aft)
else:
    pass

aft.reluctance_network.show()