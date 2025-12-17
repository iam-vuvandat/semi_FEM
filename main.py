from system.core import libraries_require
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace

re_create_motor = True

if re_create_motor == False:
    aft = workspace.load("aft1")

else:
    aft = AxialFluxMotorType1(magnet_length= 4*1e-3)
    aft.create_geometry()
    aft.create_adaptive_mesh()
    aft.create_reluctance_network()
    aft.reluctance_network.update_reluctance_network(magnetic_potential= aft.reluctance_network.magnetic_potential)
    
workspace.save(aft1 = aft)
workspace.save(aft_0_1mm = aft)

aft.reluctance_network.solve_magnetic_equation(max_iteration =4,
                                                    max_relative_residual = 1 * 1e-4,
                                                    damping_factor = 0.4,
                                                    first_step_damping_factor = 1.0,
                                                    load_step= 5,
                                                    debug = True)
aft.reluctance_network.show() 




