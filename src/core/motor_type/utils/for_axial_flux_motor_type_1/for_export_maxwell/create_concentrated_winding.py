import numpy as np 
import math
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.apply_symmetry import apply_symmetry

pi = math.pi

def create_concentrated_winding(m3d, motor):

    winding_data = motor.winding_data # extract data
    phase = winding_data.phase 
    tooth_matrix = winding_data.winding_matrix
    turns = winding_data.turns

    drive = motor.drive
    motor.update_maxwell_setting()
    current_function = motor.maxwell_export_option.current_function

    geometry_data = motor.geometry_data 

    stator = motor.geometry_data.stator
    slot_number         = stator.slot_number
    stator_lam_dia      = stator.stator_lam_dia *1e3
    stator_bore_dia     = stator.stator_bore_dia  *1e3
    slot_opening        = stator.slot_opening   *1e3
    wdg_extension_inner = stator.wdg_extension_inner   *1e3
    wdg_extension_outer = stator.wdg_extension_outer   *1e3
    slot_width          = stator.slot_width  *1e3
    slot_depth          = stator.slot_depth  *1e3
    slot_corner_radius  = stator.slot_corner_radius  
    tooth_tip_depth     = stator.tooth_tip_depth   *1e3
    tooth_tip_angle     = stator.tooth_tip_angle
    stator_length       = stator.stator_length  *1e3
    stator_outer_radius = stator_lam_dia / 2 
    stator_inner_radius = stator_bore_dia / 2
    open_arc_slot = 360 / slot_number
    half_open_arc_slot = open_arc_slot / 2 
    
    rotor = geometry_data.rotor # extract rotor
    rotor_length = rotor.rotor_length *1e3
    magnet_length = rotor.magnet_length *1e3
    airgap = rotor.airgap *1e3

    offset_z0 = rotor_length + magnet_length + airgap
    offset_z1 = offset_z0 + tooth_tip_depth
    w1 = (1/2) * (slot_width - slot_opening)
    h1 = w1 * np.tan(np.radians(tooth_tip_angle))
    offset_z2 = offset_z1 + h1
    offset_z3 = offset_z1 + slot_depth

    tooth_body_length = offset_z3 - offset_z2
    z_winding_bottom = offset_z2 + tooth_body_length / 8
    z_winding_top = offset_z3 - tooth_body_length / 8
    winding_heigh = z_winding_top - z_winding_bottom
    
    # create winding in slot 1
    base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, z_winding_bottom], radius=stator_outer_radius * 1.05, height=winding_heigh, name = "winding_base")
    hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, z_winding_bottom], radius=stator_inner_radius * 0.95, height=winding_heigh)
    m3d.modeler.subtract(blank_list=[base], tool_list=[hole], keep_originals=False)

    knife_1 = m3d.modeler.create_box(origin=[0, 0, z_winding_bottom], sizes=[stator_outer_radius * 1.06, 0.0001, winding_heigh])
    m3d.modeler.rotate(knife_1, axis="Z", angle= half_open_arc_slot * 0.95)

    knife_2 = m3d.modeler.create_box(origin=[0, 0, z_winding_bottom], sizes=[stator_outer_radius * 1.06, 0.0001, winding_heigh])
    m3d.modeler.rotate(knife_2, axis="Z", angle= -half_open_arc_slot * 0.95)

    m3d.modeler.subtract(blank_list=[base], tool_list=[knife_1, knife_2], keep_originals=False)
    segments = m3d.modeler.separate_bodies(base)

    if m3d.modeler[segments[0]].volume >= m3d.modeler[segments[1]].volume:
        m3d.modeler.delete(segments[0])
        winding_base = segments[1]
    else:
        m3d.modeler.delete(segments[1])
        winding_base = segments[0]

    base1 = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, z_winding_bottom], radius=stator_outer_radius * 1.03, height=winding_heigh)
    hole1 = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, z_winding_bottom], radius=stator_inner_radius * 0.97, height=winding_heigh)
    m3d.modeler.subtract(blank_list=[base1], tool_list=[hole1], keep_originals=False)

    knife_1 = m3d.modeler.create_box(origin=[0, 0, z_winding_bottom], sizes=[stator_outer_radius * 1.06, 0.0001, winding_heigh])
    m3d.modeler.rotate(knife_1, axis="Z", angle= half_open_arc_slot * 0.9)

    knife_2 = m3d.modeler.create_box(origin=[0, 0, z_winding_bottom], sizes=[stator_outer_radius * 1.06, 0.0001, winding_heigh])
    m3d.modeler.rotate(knife_2, axis="Z", angle= -half_open_arc_slot * 0.9)

    m3d.modeler.subtract(blank_list=[base1], tool_list=[knife_1, knife_2], keep_originals=False)
    segments_h = m3d.modeler.separate_bodies(base1)
    
    if m3d.modeler[segments_h[0]].volume >= m3d.modeler[segments_h[1]].volume:
        m3d.modeler.delete(segments_h[0])
        winding_hole = segments_h[1]
    else:
        m3d.modeler.delete(segments_h[1])
        winding_hole = segments_h[0]

    m3d.modeler.subtract(blank_list=[winding_base], tool_list=[winding_hole], keep_originals=False)
    m3d.modeler[winding_base].material_name = "copper"

    winding_cross_section = m3d.modeler.create_rectangle(orientation = "ZX", origin = [0, 0, z_winding_bottom], sizes = [winding_heigh, (stator_inner_radius + stator_outer_radius)/2], name = "winding_cross_section")
    m3d.modeler.rotate(winding_cross_section, axis="Z", angle=1.0)
    m3d.modeler.intersect(assignment = [winding_cross_section,winding_base], keep_originals=True)
    
    _, new_winding_base = m3d.modeler.duplicate_around_axis(assignment=winding_base, axis="Z", angle = open_arc_slot, clones=slot_number)
    all_winding_bases_raw = [winding_base] + list(new_winding_base)

    _, new_winding_cross_section = m3d.modeler.duplicate_around_axis(assignment=winding_cross_section, axis="Z", angle = open_arc_slot, clones=slot_number)
    all_winding_cross_section_raw = [winding_cross_section] + list(new_winding_cross_section)

    # Áp dụng symmetry cho từng bối dây và mặt cắt để lọc theo sector
    valid_winding_bases = []
    valid_cross_sections = []

    for obj in all_winding_bases_raw:
        valid_winding_bases.append(apply_symmetry(assignment=obj, m3d=m3d, motor=motor))

    for obj in all_winding_cross_section_raw:
        valid_cross_sections.append(apply_symmetry(assignment=obj, m3d=m3d, motor=motor))

    current = []
    for i in range(int(phase)):
        current_phase_i = m3d.assign_winding(winding_type='Current', is_solid=False, current=current_function[i], resistance=0, inductance=0, voltage=0, parallel_branches=1, phase=0, name=f"phase{i+1}")
        current.append(current_phase_i)

    for i in range(int(slot_number)):
        if valid_cross_sections[i] is None:
            continue
            
        for j in range(int(phase)):
            if tooth_matrix[i,j] != 0:
                if tooth_matrix[i,j] > 0:
                    direction = 'Positive'
                else:
                    direction = 'Negative'
                
                new_coil = m3d.assign_coil(valid_cross_sections[i], conductors_number= turns * np.sign(tooth_matrix[i,j]), polarity=direction)
                m3d.add_winding_coils(assignment = current[j].name, coils = new_coil.name)

    return [w for w in valid_winding_bases if w is not None]