import paths
import numpy as np
import matplotlib.pyplot as plt
import math

from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io

RE_CREATE_MOTOR = True
FILENAME        = "AFT_Motor_Optimization"

aft = AxialFluxMotorType1()
aft.calculation_data.n_point = 10
aft.just_changed("calculation_data")
aft.adaptive_mesh_data.n_r_2 = 1
aft.adaptive_mesh_data.n_r_1 = 1
aft.adaptive_mesh_data.n_r_3 = 1
aft.adaptive_mesh_data.n_z_tooth_body = 1
aft.adaptive_mesh_data.n_z_tooth_tip_2 = 1
aft.just_changed("mesh")
aft.drive_data.i_rms = 5
aft.just_changed("drive")
aft.analysis_motor()
aft.reluctance_network.show_elements()


