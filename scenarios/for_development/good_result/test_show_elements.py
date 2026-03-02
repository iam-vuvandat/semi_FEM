import paths
import numpy as np
import matplotlib.pyplot as plt
import math

from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io

RE_CREATE_MOTOR = True
FILENAME        = "AFT_Motor_Optimization"

aft = AxialFluxMotorType1()
aft.winding_data.turns = 25
aft.just_changed("winding_data")

aft.geometry_data.rotor.airgap = 1 * 1e-3
aft.geometry_data.rotor.magnet_length = 3 * 1e-3 
aft.just_changed("geometry")

aft.calculation_data.n_point = 15
aft.calculation_data.solve_cogging = True
aft.calculation_data.max_relative_residual = 0.01
aft.calculation_data.solve_only_1_step = False
aft.just_changed("calculation_data")

aft.adaptive_mesh_data.n_r_2 = 3
aft.adaptive_mesh_data.n_r_1 = 2
aft.adaptive_mesh_data.n_r_3 = 2
aft.adaptive_mesh_data.n_z_tooth_body = 3
aft.adaptive_mesh_data.n_z_tooth_tip_2 = 3
aft.just_changed("mesh")

aft.drive_data.i_rms = 5    
aft.just_changed("drive")

#aft.require("reluctance_network")
#aft.reluctance_network.get_geometric_error()
#print(aft.reluctance_network.geometric_error)

aft.analysis_motor()
#aft.reluctance_network.show_elements()
aft.display()

aft.record.plot_flux_linkage(plot = True)
aft.record.plot_back_emf(plot = True)
aft.record.plot_maxwell_stress_tensor(plot = True)

