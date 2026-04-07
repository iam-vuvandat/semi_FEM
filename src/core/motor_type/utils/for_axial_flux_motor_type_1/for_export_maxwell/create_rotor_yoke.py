import numpy as np
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.apply_symmetry import apply_symmetry

def create_rotor_yoke(motor, m3d):
    # extract geometry
    rotor = motor.geometry_data.rotor
    rotor_lam_dia        = rotor.rotor_lam_dia  * 1e3 
    shaft_hole_diameter  = rotor.shaft_hole_diameter *1e3 
    rotor_length         = rotor.rotor_length *1e3

    rotor_outer_radius = rotor_lam_dia / 2 
    rotor_inner_radius = shaft_hole_diameter / 2

    material_name = motor.material_database.iron.name

    rotor_yoke = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=rotor_outer_radius, height=rotor_length)
    rotor_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=rotor_inner_radius, height=rotor_length)
    
    m3d.modeler.subtract(blank_list=[rotor_yoke], tool_list=[rotor_hole], keep_originals=False)
    
    m3d.modeler[rotor_yoke].material_name = material_name
    m3d.modeler[rotor_yoke].name = "rotor_yoke"

    apply_symmetry(assignment=rotor_yoke, m3d=m3d, motor=motor)

    return rotor_yoke