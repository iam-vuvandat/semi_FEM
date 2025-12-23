from system.core import libraries_require
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace

re_create_motor = False

if re_create_motor == False:
    print("loading aft")
    aft = workspace.load("aft1")
    print("load aft successfully")

else:
    aft = AxialFluxMotorType1(magnet_length= 2*1e-3,
                            airgap= 3.0 * 1e-3)
    aft.create_geometry()
    aft.create_adaptive_mesh()
    aft.create_reluctance_network()
    aft.reluctance_network.update_reluctance_network(magnetic_potential= aft.reluctance_network.magnetic_potential)
    
workspace.save(aft1 = aft)
workspace.save(aft_0_1mm = aft)

aft.reluctance_network.solve_magnetic_equation(max_iteration =4,
                                               method="levenberg_marquardt",
                                               max_relative_residual = 1 * 1e-4,
                                               adaptive_damping_factor = (0.5,0.1),
                                               load_step= 6,
                                               debug = True)
aft.reluctance_network.show() 

aft.reluctance_network.solve_magnetic_equation(max_iteration =4,
                                               method="direct_optimization",
                                               max_relative_residual = 1 * 1e-4,
                                               adaptive_damping_factor = (0.5,0.1),
                                               load_step= 6,
                                               debug = True)
aft.reluctance_network.show() 

aft.reluctance_network.solve_magnetic_equation(max_iteration =5,
                                               method="fixed_point_iteration",
                                               max_relative_residual = 1 * 1e-4,
                                               adaptive_damping_factor = (0.5,0.1),
                                               load_step= 10,
                                               debug = True)
aft.reluctance_network.show() 




