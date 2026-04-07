import numpy as np
import math
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.apply_symmetry import apply_symmetry

def create_magnet(motor, m3d):

    # extract geometry
    rotor = motor.geometry_data.rotor
    pole_number          = rotor.pole_number 
    rotor_lam_dia        = rotor.rotor_lam_dia  * 1e3 
    magnet_arc           = rotor.magnet_arc 
    magnet_embed_depth   = rotor.magnet_embed_depth * 1e3
    magnet_depth         = rotor.magnet_depth * 1e3 
    magnet_segments      = rotor.magnet_segments
    banding_depth        = rotor.banding_depth * 1e-3 
    shaft_dia            = rotor.shaft_dia *1e3
    shaft_hole_diameter  = rotor.shaft_hole_diameter *1e3 
    airgap               = rotor.airgap *1e3
    magnet_length        = rotor.magnet_length *1e3
    rotor_length         = rotor.rotor_length *1e3

    rotor_outer_radius = rotor_lam_dia / 2 
    rotor_inner_radius = shaft_hole_diameter / 2
    magnet_radius = rotor_outer_radius - magnet_embed_depth
    magnet_hole_radius = magnet_radius - magnet_depth

    magnet_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, rotor_length], radius=magnet_radius, height=magnet_length)
    magnet_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, rotor_length], radius=magnet_hole_radius, height=magnet_length)
    m3d.modeler.subtract(blank_list=[magnet_base], tool_list=[magnet_hole], keep_originals=False)

    pole_arc = 360 / pole_number
    magnet_arc_mechanical = pole_arc * (magnet_arc/180)
    half_magnet_arc_mechanical = magnet_arc_mechanical / 2 

    knife_1 = m3d.modeler.create_box(origin=[0, 0, rotor_length], sizes=[magnet_radius, 0.0001, magnet_length])
    m3d.modeler.rotate(knife_1, axis="Z", angle=half_magnet_arc_mechanical)
    knife_2 = m3d.modeler.create_box(origin=[0, 0, rotor_length], sizes=[magnet_radius, 0.0001, magnet_length])
    m3d.modeler.rotate(knife_2, axis="Z", angle=-half_magnet_arc_mechanical)
    m3d.modeler.subtract(blank_list=[magnet_base], tool_list=[knife_1, knife_2], keep_originals=False)
    
    magnet_segments_list = m3d.modeler.separate_bodies(magnet_base)

    if m3d.modeler[magnet_segments_list[0]].volume >= m3d.modeler[magnet_segments_list[1]].volume:
        m3d.modeler.delete(magnet_segments_list[0])
        magnet_pole = magnet_segments_list[1]
    else:
        m3d.modeler.delete(magnet_segments_list[1])
        magnet_pole = magnet_segments_list[0]

    magnet_material_type = motor.material_database.magnet
    material_name = magnet_material_type.name
    coercivity = magnet_material_type.coercivity
    
    m3d.modeler[magnet_pole].name = "magnet_pole"
    magnet_pole = "magnet_pole"

    name_n = f"{material_name}N"
    name_s = f"{material_name}S"

    if name_n not in m3d.materials.material_keys:
        mat_n = m3d.materials.add_material(name_n)
        mat_n.set_magnetic_coercivity(-coercivity, 0, 0, 1)
    
    if name_s not in m3d.materials.material_keys:
        mat_s = m3d.materials.add_material(name_s)
        mat_s.set_magnetic_coercivity(-coercivity, 0, 0, -1)

    m3d.modeler[magnet_pole].material_name = name_n

    arc_pole = 360 / pole_number
    _, new_poles = m3d.modeler.duplicate_around_axis(assignment=magnet_pole, axis="Z", angle=arc_pole, clones=pole_number)
    
    for i in range(len(new_poles)):
        m3d.modeler[new_poles[i]].material_name = name_s if i % 2 == 0 else name_n

    all_magnets_raw = [magnet_pole] + list(new_poles)
    magnets_in_sector = []

    for mag in all_magnets_raw:
        res = apply_symmetry(assignment=mag, m3d=m3d, motor=motor)
        if res:
            magnets_in_sector.append(res)

    return magnets_in_sector