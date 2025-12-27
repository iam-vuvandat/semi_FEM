import paths
from system.core import libraries_require
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace  

re_create_motor = False

if re_create_motor == False:
    print("loading aft")
    aft = workspace.load("aft1")
    print("load aft successfully")

else:
    aft = AxialFluxMotorType1(magnet_length= 4.0 *1e-3,
                            airgap= 0.5 * 1e-3)
    aft.create_geometry()
    aft.create_adaptive_mesh()
    aft.create_reluctance_network()
    aft.reluctance_network.update_reluctance_network(magnetic_potential= aft.reluctance_network.magnetic_potential)

workspace.save(aft1 = aft)
