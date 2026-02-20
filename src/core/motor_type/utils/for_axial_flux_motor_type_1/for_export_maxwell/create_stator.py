import numpy as np

def create_stator(motor,m3d):
    # extract geometry
    rotor = motor.geometry_data.rotor
    pole_number          = rotor.pole_number 
    rotor_lam_dia        = rotor.rotor_lam_dia  * 1e3 
    magnet_arc           = rotor.magnet_arc 
    magnet_embed_depth   = rotor.magnet_embed_depth  
    magnet_depth         = rotor.magnet_depth * 1e3 
    magnet_segments      = rotor.magnet_segments
    banding_depth        = rotor.banding_depth
    shaft_dia            = rotor.shaft_dia *1e3
    shaft_hole_diameter  = rotor.shaft_hole_diameter *1e3 
    airgap               = rotor.airgap *1e3
    magnet_length        = rotor.magnet_length *1e3
    rotor_length         = rotor.rotor_length *1e3

    rotor_outer_radius = rotor_lam_dia / 2 
    rotor_inner_radius = shaft_hole_diameter / 2
    magnet_radius = rotor_outer_radius - magnet_embed_depth
    magnet_hole   = magnet_radius - magnet_depth

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

    offset_z0 = rotor_length + magnet_length + airgap
    stator_outer_radius = stator_lam_dia / 2 
    stator_inner_radius = stator_bore_dia / 2

    material_name = motor.material_database.iron.name

    ### tooth tip 1 
    tooth_tip_1_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, offset_z0], radius=stator_outer_radius, height=tooth_tip_depth)
    tooth_tip_1_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, offset_z0], radius=stator_inner_radius, height=tooth_tip_depth)
    m3d.modeler.subtract(blank_list=[tooth_tip_1_base], tool_list=[tooth_tip_1_hole], keep_originals=False)
    m3d.modeler[tooth_tip_1_base].material_name = material_name

    slot_arc = 360 / slot_number
    half_slot_opening = slot_opening / 2

    knife_1 = m3d.modeler.create_box(origin=[0, -half_slot_opening, offset_z0], sizes=[stator_outer_radius * 1.5, slot_opening, tooth_tip_depth])
    m3d.modeler.rotate(knife_1, axis="Z", angle=slot_arc / 2)

    knife_2 = m3d.modeler.create_box(origin=[0, -half_slot_opening, offset_z0], sizes=[stator_outer_radius * 1.5, slot_opening, tooth_tip_depth])
    m3d.modeler.rotate(knife_2, axis="Z", angle=-slot_arc / 2)

    m3d.modeler.subtract(blank_list=[tooth_tip_1_base], tool_list=[knife_1, knife_2], keep_originals=False)
    tooth_tip_segments = m3d.modeler.separate_bodies(tooth_tip_1_base)

    if tooth_tip_segments[0].volume <= tooth_tip_segments[1].volume:
        m3d.modeler.delete(tooth_tip_segments[1])
        tooth_tip_1 = tooth_tip_segments[0]
    else:
        m3d.modeler.delete(tooth_tip_segments[0])
        tooth_tip_1 = tooth_tip_segments[1]
    m3d.modeler[tooth_tip_1].name = "tooth_tip_1"

    ### tooth_tip_2 
    z_bottom_surface = offset_z0 + tooth_tip_depth
    w1 = (1/2) * (slot_width - slot_opening)
    h1 = w1 * np.tan(np.radians(tooth_tip_angle))
    z_top_surface = z_bottom_surface + h1

    C_in_per_slot = (stator_bore_dia * np.pi) / slot_number
    angle_in_mouth = 2 * np.arctan((C_in_per_slot - slot_opening) / stator_bore_dia)
    angle_out_mouth = 2 * np.arctan(((stator_lam_dia * np.pi / slot_number) - slot_opening) / stator_lam_dia)

    p1_in_b = [stator_bore_dia/2 * np.cos(-angle_in_mouth/2), stator_bore_dia/2 * np.sin(-angle_in_mouth/2), z_bottom_surface]
    p2_in_b = [stator_bore_dia/2, 0, z_bottom_surface]
    p3_in_b = [stator_bore_dia/2 * np.cos(angle_in_mouth/2), stator_bore_dia/2 * np.sin(angle_in_mouth/2), z_bottom_surface]
    arc_in_b = m3d.modeler.create_polyline(points=[p1_in_b, p2_in_b, p3_in_b], segment_type="Arc")

    p1_out_b = [stator_lam_dia/2 * np.cos(-angle_out_mouth/2), stator_lam_dia/2 * np.sin(-angle_out_mouth/2), z_bottom_surface]
    p2_out_b = [stator_lam_dia/2, 0, z_bottom_surface]
    p3_out_b = [stator_lam_dia/2 * np.cos(angle_out_mouth/2), stator_lam_dia/2 * np.sin(angle_out_mouth/2), z_bottom_surface]
    arc_out_b = m3d.modeler.create_polyline(points=[p1_out_b, p2_out_b, p3_out_b], segment_type="Arc")

    res_b = m3d.modeler.connect([arc_in_b, arc_out_b])
    bottom_sheet = res_b[0] if isinstance(res_b, list) else res_b

    angle_in_slot = 2 * np.arctan((C_in_per_slot - slot_width) / stator_bore_dia)
    angle_out_slot = 2 * np.arctan(((stator_lam_dia * np.pi / slot_number) - slot_width) / stator_lam_dia)

    p1_in_t = [stator_bore_dia/2 * np.cos(-angle_in_slot/2), stator_bore_dia/2 * np.sin(-angle_in_slot/2), z_top_surface]
    p2_in_t = [stator_bore_dia/2, 0, z_top_surface]
    p3_in_t = [stator_bore_dia/2 * np.cos(angle_in_slot/2), stator_bore_dia/2 * np.sin(angle_in_slot/2), z_top_surface]
    arc_in_t = m3d.modeler.create_polyline(points=[p1_in_t, p2_in_t, p3_in_t], segment_type="Arc")

    p1_out_t = [stator_lam_dia/2 * np.cos(-angle_out_slot/2), stator_lam_dia/2 * np.sin(-angle_out_slot/2), z_top_surface]
    p2_out_t = [stator_lam_dia/2, 0, z_top_surface]
    p3_out_t = [stator_lam_dia/2 * np.cos(angle_out_slot/2), stator_lam_dia/2 * np.sin(angle_out_slot/2), z_top_surface]
    arc_out_t = m3d.modeler.create_polyline(points=[p1_out_t, p2_out_t, p3_out_t], segment_type="Arc")

    res_t = m3d.modeler.connect([arc_in_t, arc_out_t])
    top_sheet = res_t[0] if isinstance(res_t, list) else res_t

    res_tip2 = m3d.modeler.connect([bottom_sheet, top_sheet])
    tooth_tip_2 = res_tip2[0] if isinstance(res_tip2, list) else res_tip2
    m3d.modeler[tooth_tip_2].name = "tooth_tip_2"
    m3d.modeler[tooth_tip_2].material_name = material_name

    ### tooth_body
    tooth_body_length = slot_depth - h1
    all_faces_tip2 = m3d.modeler.get_object_faces("tooth_tip_2")
    top_face_id = None
    z_max_tip2 = -1e9
    for f_id in all_faces_tip2:
        v_ids = m3d.modeler.get_face_vertices(f_id)
        if v_ids:
            z_pos = m3d.modeler.get_vertex_position(v_ids[0])
            if z_pos[2] > z_max_tip2:
                z_max_tip2 = z_pos[2]
                top_face_id = f_id

    res_body_sheet = m3d.modeler.create_object_from_face(assignment=top_face_id)
    body_sheet = res_body_sheet[0] if isinstance(res_body_sheet, list) else res_body_sheet

    sweep_body = m3d.modeler.sweep_along_vector(assignment=body_sheet, sweep_vector=[0, 0, tooth_body_length])
    tooth_body = sweep_body[0] if isinstance(sweep_body, list) else sweep_body
    m3d.modeler[tooth_body].name = "tooth_body"
    m3d.modeler[tooth_body].material_name = material_name

    # --- Nhân bản cụm răng ---
    _, new_teeth = m3d.modeler.duplicate_around_axis(
        assignment=["tooth_tip_1", "tooth_tip_2", "tooth_body"],
        axis="Z",
        angle=slot_arc,
        clones=slot_number
    )

    ### stator yoke
    yoke_height = stator_length - tooth_tip_depth - slot_depth
    z_yoke = offset_z0 + tooth_tip_depth + slot_depth

    stator_yoke = m3d.modeler.create_cylinder(
        orientation="Z", 
        origin=[0, 0, z_yoke], 
        radius=stator_outer_radius, 
        height=yoke_height
    )

    stator_yoke_hole = m3d.modeler.create_cylinder(
        orientation="Z", 
        origin=[0, 0, z_yoke], 
        radius=stator_inner_radius, 
        height=yoke_height
    )

    m3d.modeler.subtract(blank_list=[stator_yoke], tool_list=[stator_yoke_hole], keep_originals=False)
    m3d.modeler[stator_yoke].name = "stator_yoke"
    m3d.modeler[stator_yoke].material_name = material_name

    # Unite all stator components
    stator_parts = ["tooth_tip_1", "tooth_tip_2", "tooth_body", "stator_yoke"] + new_teeth
    m3d.modeler.unite(assignment=stator_parts)
    m3d.modeler[stator_parts[0]].name = "stator"