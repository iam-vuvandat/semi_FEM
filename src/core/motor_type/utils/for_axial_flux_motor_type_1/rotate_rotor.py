import numpy as np

def rotate_rotor(motor, n_step):
    """
    Rotates the rotor layers within the Reluctance Network by a specified number of steps.
    Updated to use the refactored adaptive_mesh_data structure.
    """
    # 1. Access the mesh data container from the motor's mesh object
    # Since CylindricalMesh now stores the refactored Container
    adaptive_mesh_data = motor.mesh.adaptive_mesh_data
    
    # 2. Extract discretization parameters using long-form names
    nodes_axial_inner_air   = adaptive_mesh_data.nodes_axial_inner_air
    nodes_axial_rotor_yoke  = adaptive_mesh_data.nodes_axial_rotor_yoke
    nodes_axial_magnet      = adaptive_mesh_data.nodes_axial_magnet

    # 3. Calculate the number of axial layers to be rotated
    # The logic (sum of nodes - 3) is preserved exactly as original
    number_of_layers_to_rotate = (nodes_axial_inner_air + 
                                  nodes_axial_rotor_yoke + 
                                  nodes_axial_magnet - 3)
    
    # 4. Generate the range of Z-axis indices that belong to the rotor assembly
    z_indices_to_rotate = np.arange(number_of_layers_to_rotate)
    
    # 5. Execute the rotation in the Reluctance Network solver core
    reluctance_network = motor.reluctance_network
    reluctance_network.rotate(z_indices = z_indices_to_rotate,
                              n_step    = n_step)