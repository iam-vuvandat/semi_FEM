def create_moving_band(motor, m3d):

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

    moving_band = m3d.modeler.create_cylinder(
        orientation="Z", 
        origin=[0, 0, - rotor_length], 
        radius= rotor_outer_radius * 1.1, 
        height= 2 * rotor_length + magnet_length + airgap * 0.5
    )

    m3d.modeler[moving_band].name = "moving_band"
    m3d.modeler[moving_band].material_name = "vacuum"
    motion_setup = m3d.assign_rotate_motion(assignment="moving_band", angular_velocity="1500rpm")
    motion_setup.props["BandMappingAngle"] = "1deg"

    rotating_parts = m3d.modeler.object_names[:]
    m3d.eddy_effects_on(rotating_parts, enable_eddy_effects=False)