import numpy as np
import math
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_distributed_winding import create_distributed_winding
from src.core.motor_type.utils.for_create_geometry.rotate_point_z import rotate_point_z
from src.core.motor_type.utils.for_export_maxwell.create_conductor import create_conductor
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_concentrated_winding import create_concentrated_winding


def create_winding(m3d,motor):
    
    throw = motor.winding_data.throw

    if throw == 1: # concentrated winding
        return create_concentrated_winding(m3d = m3d, motor= motor)
    else: # distributed winding
        return create_distributed_winding(m3d = m3d, motor = motor)
