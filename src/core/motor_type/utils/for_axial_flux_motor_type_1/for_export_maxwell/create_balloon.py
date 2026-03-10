
def create_balloon(motor,pad_value=30,m3d = None):

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

    region = m3d.modeler.create_region(pad_value= pad_value, pad_type="Percentage Offset",name = "region")
    m3d.assign_insulating(assignment=[region])