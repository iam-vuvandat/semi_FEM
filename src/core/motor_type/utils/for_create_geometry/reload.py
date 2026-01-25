def reload(motor):
    motor.find_symmetry_factor()
    motor.find_winding_matrix()
    motor.reset_record()

    motor.geometry = None
    motor.create_geometry(rotor_angle_offset = 0,
                          stator_angle_offset = 0,
                          create_rotor_yoke = True,
                          create_magnet = True,
                          create_tooth = True,
                          create_stator_yoke = True)
    motor.mesh     = None
    motor.create_adaptive_mesh()
    #motor.reluctance_network = None

