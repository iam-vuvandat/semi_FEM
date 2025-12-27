import numpy as np

def rotate_rotor(motor,n_step):
    mesh_detail_parameter = motor.mesh.detail_parameter
    n_z_in_air = mesh_detail_parameter[6]
    n_z_rotor_yoke = mesh_detail_parameter[7]
    n_z_magnet = mesh_detail_parameter[8]

    number_of_layer_rotated = n_z_in_air + n_z_rotor_yoke + n_z_magnet - 3 
    z_indices_rotate = np.arange(number_of_layer_rotated)
    
    reluctance_network = motor.reluctance_network
    reluctance_network.rotate(z_indices = z_indices_rotate,
                              n_step = n_step)