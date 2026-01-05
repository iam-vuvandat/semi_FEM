from core_class.models.MagneticPotential import MagneticPotential
import numpy as np 

def create_magnetic_potential(reluctance_network):
    periodic_boundary = reluctance_network.mesh.periodic_boundary

    if reluctance_network.magnetic_potential == None:
        number_of_element_r = reluctance_network.mesh.n_cells_r
        number_of_element_t = reluctance_network.mesh.n_cells_t
        number_of_element_z = reluctance_network.mesh.n_cells_z
        
        data = np.zeros((number_of_element_r,number_of_element_t,number_of_element_z),order='F')

    return MagneticPotential(data= data,
                             periodic_boundary = periodic_boundary)