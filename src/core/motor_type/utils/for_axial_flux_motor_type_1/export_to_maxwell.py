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

def export_to_maxwell(motor):
    
    init_window()
    m3d = init_project(project_name= "AxialFluxMotor_pyaedt", solution_type= "Transient")

    rotor = motor.geometry_data.rotor
    pole_number          = rotor.pole_number 
    rotor_lam_dia        = rotor.rotor_lam_dia  * 1e3 # (m-> mm)
    magnet_arc           = rotor.magnet_arc # (Deg)
    magnet_embed_depth   = rotor.magnet_embed_depth  
    magnet_depth         = rotor.magnet_depth * 1e3 
    magnet_segments      = rotor.magnet_segments
    banding_depth        = rotor.banding_depth
    shaft_dia            = rotor.shaft_dia *1e3
    shaft_hole_diameter  = rotor.shaft_hole_diameter *1e3 
    airgap               = rotor.airgap *1e3
    magnet_length        = rotor.magnet_length *1e3
    rotor_length         = rotor.rotor_length *1e3

    create_rotor_yoke(motor = motor, m3d = m3d )
    create_magnet(motor= motor, m3d= m3d)
    create_moving_band(motor = motor, m3d = m3d)
    create_stator(motor= motor, m3d = m3d)
    create_winding(motor= motor, m3d= m3d)
    
    create_balloon(pad_value= 10, m3d = m3d)

    
    # Mesh
    all_objects = m3d.modeler.object_names
    mesh_targets = [
        obj for obj in all_objects 
        if obj != "region"              
        and "Line" not in obj        
        and "Sheet" not in obj      
    ]

    maximum_element_length = magnet_length *2 
    m3d.mesh.assign_length_mesh(
        assignment=mesh_targets,
        maximum_length=f"{maximum_element_length}mm",
        maximum_elements=None,
        name="Global_Core_Mesh"
    )

    # Setup Analysis
    setup_name = "Setup1"

    if setup_name in m3d.setup_names:
        m3d.delete_setup(setup_name)
    
    setup = m3d.create_setup(name=setup_name, setup_type="Transient")
    
    setup.props["StopTime"] = "10ms"
    setup.props["TimeStep"] = "2ms"
    
    setup.props["SaveFieldsType"] = "Every N Steps"
    setup.props["N Steps"] = "1"
    setup.props["Steps From"] = "0s"
    setup.props["Steps To"] = "10ms"

    setup.props["NonlinearSolverResidual"] = "0.005"
    setup.props["ScalarPotential"] = "Second Order"
    setup.props["SmoothBHCurve"] = False

    setup.update()
    m3d.save_project()

    # Run
    #m3d.analyze_setup(setup_name)

    return None

    

if __name__ == "__main__":
    from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
    motor = AxialFluxMotorType1()
    motor.winding_data.throw = 2
    motor.export_to_maxwell()


    