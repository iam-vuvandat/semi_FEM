import paths
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace 
from tqdm import tqdm

re_create_motor = False
re_solve = True

if re_create_motor == False:
    print("loading aft")
    aft = workspace.load("aft1")
    print("load aft successfully")
    if re_solve == False:
        pass
    else:
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
    workspace.save(aft1=aft)



if re_solve == True:
    n_theta = aft.mesh.detail_parameter[5] - 1 
    n_step_shift = 3
    n_step_solve = n_theta // n_step_shift

    for i in range(1):
        aft.reluctance_network.fixed_point_iteration()
        

    workspace.save(aft1=aft)
else:
    pass

aft.reluctance_network.show()