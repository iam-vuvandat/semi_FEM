import paths
from system.core import libraries_require
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace  

re_create_motor = False

if re_create_motor == False:
    print("loading aft")
    aft = workspace.load("aft1")
    print("load aft successfully")
    aft.reluctance_network.list_elements_lite = None

else:
    aft = AxialFluxMotorType1(magnet_length= 4.0 *1e-3,
                            airgap= 0.5 * 1e-3)
    aft.create_geometry()
    aft.create_adaptive_mesh()
    aft.create_reluctance_network()
    aft.reluctance_network.update_reluctance_network(magnetic_potential= aft.reluctance_network.magnetic_potential)
    
n_step_rotate = 10

for i in range(aft.mesh.detail_parameter[5]// n_step_rotate):
    print(i,"  ",aft.mesh.detail_parameter[5],"  ",n_step_rotate)
    aft.reluctance_network.solve_magnetic_equation()
    aft.rotate_rotor(n_step = n_step_rotate)

workspace.save(aft1 = aft)
aft.reluctance_network.show()

    