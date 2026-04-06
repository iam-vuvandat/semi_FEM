import paths
import numpy as np
import math 
pi = math.pi

from src.core.motor_type.utils.for_export_maxwell.init_window import init_window
from src.core.motor_type.utils.for_export_maxwell.init_project import init_project
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_rotor_yoke import create_rotor_yoke
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_magnet import create_magnet
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_moving_band import create_moving_band
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.setup_axial_force_calculation import setup_axial_force_calculation
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_custom_mesh import create_custom_mesh
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_stator import create_stator
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_winding import create_winding
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_balloon import create_balloon
from src.core.motor_type.utils.for_export_maxwell.solve_standard_step import solve_standard_step

def export_to_maxwell(motor, callback=None):
    
    init_window()
    m3d = init_project(project_name="AxialFluxMotor_pyaedt", solution_type="Transient", motor = motor)
    motor.require("mesh")
    rotor_yoke = create_rotor_yoke(motor=motor, m3d=m3d)
    magnet_segments =  create_magnet(motor=motor, m3d=m3d)
    moving_band =  create_moving_band(motor=motor, m3d=m3d)
    print(moving_band)
    setup_axial_force_calculation(m3d = m3d, assignment= moving_band)
    stator = create_stator(motor=motor, m3d=m3d)
    create_winding(motor=motor, m3d=m3d)
    region = create_balloon(motor = motor, m3d=m3d)
    create_custom_mesh(m3d = m3d, motor = motor, region = region )

    
    solve_standard_step(m3d = m3d, motor = motor)
    m3d.save_project()

    return None

    