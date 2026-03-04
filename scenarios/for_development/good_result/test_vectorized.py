import paths
import time

from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1

aft = AxialFluxMotorType1()
aft = AxialFluxMotorType1()
aft.winding_data.turns = 25
aft.just_changed("winding_data")

aft.geometry_data.rotor.airgap = 1 * 1e-3
aft.geometry_data.rotor.magnet_length = 3 * 1e-3 
aft.just_changed("geometry")

aft.calculation_data.n_point = 10
aft.calculation_data.solve_cogging = True
aft.calculation_data.max_relative_residual = 0.005
aft.calculation_data.solve_only_1_step = False
aft.just_changed("calculation_data")

aft.adaptive_mesh_data.n_r_2 = 3
aft.adaptive_mesh_data.n_theta = 40
aft.adaptive_mesh_data.n_r_1 = 2
aft.adaptive_mesh_data.n_r_3 = 2
aft.adaptive_mesh_data.n_z_tooth_body = 3
aft.adaptive_mesh_data.n_z_tooth_tip_2 = 3
aft.just_changed("mesh")
aft.require("mesh")
aft.require("reluctance_network")

start_time = time.time()
aft.reluctance_network.solve()
print(f"Solve execution time: {time.time() - start_time:.4f} s")

