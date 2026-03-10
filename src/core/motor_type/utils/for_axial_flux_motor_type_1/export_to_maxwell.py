import paths
import numpy as np
import math 
pi = math.pi

from src.core.motor_type.utils.for_create_geometry.rotate_point_z import rotate_point_z
from src.core.motor_type.utils.for_export_maxwell.init_window import init_window
from src.core.motor_type.utils.for_export_maxwell.init_project import init_project
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_rotor_yoke import create_rotor_yoke
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_magnet import create_magnet
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_moving_band import create_moving_band
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_stator import create_stator
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_winding import create_winding
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_balloon import create_balloon
from src.core.motor_type.utils.for_export_maxwell.init_solver import init_solver

def export_to_maxwell(motor, callback=None):
    
    init_window()
    m3d = init_project(project_name="AxialFluxMotor_pyaedt", solution_type="Transient")
    rotor = motor.geometry_data.rotor
    magnet_length = rotor.magnet_length * 1e3
    
    # require
    motor.require("mesh")

    # create geometry
    segment_created = []
    rotor_yoke = create_rotor_yoke(motor=motor, m3d=m3d)
    segment_created.append(rotor_yoke)
    
    magnet_segments =  create_magnet(motor=motor, m3d=m3d)
    segment_created += magnet_segments
    
    create_moving_band(motor=motor, m3d=m3d)
    
    create_stator(motor=motor, m3d=m3d)
    
    create_winding(motor=motor, m3d=m3d)
    
    create_balloon(pad_value=10, m3d=m3d)

    all_objects = m3d.modeler.object_names
    mesh_targets = [
        obj for obj in all_objects 
        if obj != "region"               
        and "Line" not in obj        
        and "Sheet" not in obj      
    ]

    if callback: callback("Assigning mesh", 85)
    maximum_element_length = magnet_length * 2 
    m3d.mesh.assign_length_mesh(
        assignment=mesh_targets,
        maximum_length=f"{maximum_element_length}mm",
        maximum_elements=None,
        name="Global_Core_Mesh"
    )

    init_solver(m3d = m3d, motor = motor)
    m3d.save_project()


    return None

if __name__ == "__main__":
    from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
    motor = AxialFluxMotorType1()
    export_to_maxwell(motor)
    