import numpy as np

def rotate_rotor(motor,n_step):
    adaptive_mesh_data = motor.mesh.adaptive_mesh_data
    n_z_in_air = adaptive_mesh_data.n_z_in_air
    n_z_rotor_yoke = adaptive_mesh_data.n_z_rotor_yoke
    n_z_magnet = adaptive_mesh_data.n_z_magnet

    number_of_layer_rotated = n_z_in_air + n_z_rotor_yoke + n_z_magnet - 3 
    z_indices_rotate = np.arange(number_of_layer_rotated)
    
    reluctance_network = motor.reluctance_network
    reluctance_network.rotate(z_indices = z_indices_rotate,
                              n_step = n_step)