def create_rotor_yoke(motor,m3d):
    # extract geometry
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

    rotor_outer_radius = rotor_lam_dia / 2 
    rotor_inner_radius = shaft_hole_diameter / 2

    material_name = motor.material_database.iron.name

    rotor_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=rotor_outer_radius, height=rotor_length)
    rotor_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=rotor_inner_radius, height=rotor_length)
    m3d.modeler.subtract(blank_list=[rotor_base], tool_list=[rotor_hole], keep_originals=False)
    m3d.modeler[rotor_base].material_name = material_name
    m3d.modeler[rotor_base].name = "rotor_yoke"

    return rotor_base



