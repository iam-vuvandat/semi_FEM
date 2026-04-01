import math

def create_moving_band(motor, m3d):

    # extract geometry
    rotor = motor.geometry_data.rotor
    rotor_lam_dia        = rotor.rotor_lam_dia  * 1e3 
    airgap               = rotor.airgap *1e3
    magnet_length        = rotor.magnet_length *1e3
    rotor_length         = rotor.rotor_length *1e3

    rotor_outer_radius = rotor_lam_dia / 2 
    
    # create moving band
    moving_band = m3d.modeler.create_cylinder(
        orientation="Z", 
        origin=[0, 0, - rotor_length], 
        radius= rotor_outer_radius * 1.1, 
        height= 2 * rotor_length + magnet_length + airgap * 0.5
    )

    # band mapping angle (rotate step angle)
    maxwell_export_option = motor.maxwell_export_option
    use_default_option = maxwell_export_option.use_default_option

    
    if not use_default_option:
        custom_option = maxwell_export_option.custom_option

        # mesh setting 
        mesh_setting = custom_option.mesh_setting
        band_mapping_angle = mesh_setting.band_mapping_angle * 180 / math.pi
        band_mapping_angle = f"{band_mapping_angle}deg"

        # shaft speed
        motion_setting = custom_option.motion_setting
        shaft_speed = f"{motion_setting.shaft_speed}rpm"

    else:
        # mesh setting 
        delta_theta = motor.mesh.delta_theta # rad
        delta_theta *= 180 / math.pi
        band_mapping_angle = f"{delta_theta}deg"
        
        # shaft speed
        shaft_speed = motor.mechanical_data.shaft_speed # rpm 
        shaft_speed = f"{shaft_speed}rpm"

    print(f"band mapping angel:{band_mapping_angle}")
    print(f"shaft_speed: {shaft_speed}")

    m3d.modeler[moving_band].name = "moving_band"
    m3d.modeler[moving_band].material_name = "vacuum"
    motion_setup = m3d.assign_rotate_motion(assignment="moving_band", angular_velocity= shaft_speed)
    motion_setup.props["BandMappingAngle"] = band_mapping_angle

    rotating_parts = m3d.modeler.object_names[:]
    m3d.eddy_effects_on(rotating_parts, enable_eddy_effects=False)

    return moving_band


