import numpy as np 

def airgap_flux_density_export(motor):

    # extract mesh data 
    mesh = motor.adaptive_mesh_data
    
    # define the path_sweep
    r_layer = mesh.n_r_in + mesh.n_r_1 + (mesh.n_r_2//2)
    r_layer -= 1 # offset index 
    if mesh.n_r_2 %2 != 0: 
        r_layer +=1

    
    z_layer = mesh.n_z_in_air + mesh.n_z_rotor_yoke + mesh.n_z_magnet + (mesh.n_z_airgap //2)
    z_layer -= 1 # offset index 
    if mesh.n_z_airgap %2 != 0 : 
        z_layer += 1

    path_sweep = [r_layer,-1,z_layer]

    # run the method 
    airgap_flux_density_data = motor.reluctance_network.export_airgap_flux_density(path_sweep = path_sweep)

    # refine the last collumn 
    total_arc = (2 * np.pi) / motor.mechanical.symmetry_factor
    _,number_of_collumn = airgap_flux_density_data.shape

    airgap_flux_density_data[4, :] = np.linspace(0, total_arc, number_of_collumn)
    
    return airgap_flux_density_data