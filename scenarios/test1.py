import paths
from system.core import libraries_require
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace 
from tqdm import tqdm

re_create_motor = False
re_solve = True

if re_create_motor == False:
    print("loading aft")
    aft = workspace.load("aft1")
    print("load aft successfully")
    aft.reluctance_network.list_elements_lite = None
else:
    aft = AxialFluxMotorType1(magnet_length=4.0 * 1e-3,
                              airgap=0.5 * 1e-3)
    aft.create_geometry()
    aft.create_adaptive_mesh()
    aft.create_reluctance_network()
    aft.reluctance_network.update_reluctance_network(magnetic_potential=aft.reluctance_network.magnetic_potential)

if re_solve == True:
    n_theta = aft.mesh.detail_parameter[5] - 1 
    n_step_shift = 5
    n_step_solve = n_theta // n_step_shift

    for i in tqdm(range(int(n_step_solve)), desc="Solving & Rotating"):
        aft.reluctance_network.solve_magnetic_equation()
        aft.rotate_rotor(n_step=n_step_shift)

    workspace.save(aft1=aft)
else:
    pass

aft.reluctance_network.show()