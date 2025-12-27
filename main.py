from system.core import libraries_require
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace  

re_create_motor = False

if re_create_motor == False:
    print("loading aft")
    aft = workspace.load("aft1")
    aft.reluctance_network.list_elements_lite = None
    print("load aft successfully")

else:
    aft = AxialFluxMotorType1(magnet_length= 4.0 *1e-3,
                            airgap= 0.5 * 1e-3)
    aft.create_geometry()
    aft.create_adaptive_mesh()
    aft.create_reluctance_network()
    aft.reluctance_network.update_reluctance_network(magnetic_potential= aft.reluctance_network.magnetic_potential)
    
workspace.save(aft1 = aft)


method_test = ["conjugate_gradient"]
figure = []

max_iteration = 10
max_relative_residual = 1 * 1e-4
adaptive_damping_factor = (0.1,0.1)
load_step= 1
debug = True

for method in method_test:
    print(method)
    aft.reluctance_network.solve_magnetic_equation(max_iteration = max_iteration,
                                                   method= method,
                                                   max_relative_residual = max_relative_residual,
                                                   adaptive_damping_factor = adaptive_damping_factor,
                                                   load_step=load_step,
                                                   debug = debug)
    aft.reluctance_network.show()

    