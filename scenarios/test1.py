import paths
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace 
from tqdm import tqdm
import numpy as np

re_create_motor = True
re_solve = True

if re_create_motor == False:
    aft = workspace.load("aft1")
    if re_solve == True:
        aft.reluctance_network.list_elements_lite = None
else:
    aft = AxialFluxMotorType1(magnet_length=4.0 * 1e-3,
                              airgap=0.5 * 1e-3)
    aft.create_geometry()
    aft.create_adaptive_mesh()
    
    aft.create_reluctance_network()
    print(aft.reluctance_network.system_variable)
    print(aft.reluctance_network.loop_flux)
    aft.reluctance_network.update_reluctance_network(loop_flux=aft.reluctance_network.loop_flux)
    



if re_solve == True:
    aft.reluctance_network.fixed_point_iteration()

aft.reluctance_network.show()
