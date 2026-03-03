import numpy as np 
from src.core.core_class.utils.for_vectorized_elements.find_neighbor_indices import find_neighbor_indices

def create_vectorized_elements(vectorized_elements):
    reluctance_network = vectorized_elements.reluctance_network
    elements = reluctance_network.elements
    total_elements = elements.size
    phase_number = elements[0,0,0].element_winding_vector.size
    
    # periodic boundary 
    vectorized_elements.periodic_boundary = reluctance_network.mesh.periodic_boundary

    # virtual shape
    vectorized_elements.virtual_shape = elements.shape

    # neighbor index and valid mask
    vectorized_elements.neighbor_indices , vectorized_elements.neighbor_valid = find_neighbor_indices(vectorized_elements= vectorized_elements)

    # material
    vectorized_elements.material = np.zeros(total_elements)

    # dimension
    vectorized_elements.length   = np.zeros((6,total_elements))
    vectorized_elements.section_area = np.zeros((6,total_elements))

    # magnetic source
    vectorized_elements.magnet_source = np.zeros((6,total_elements))
    vectorized_elements.element_winding_vector = np.zeros((phase_number,total_elements))
    vectorized_elements.winding_current = reluctance_network.winding_current
    vectorized_elements.winding_source = np.zeros((6,total_elements))
    vectorized_elements.magnetic_source = np.zeros((6,total_elements))

    # reluctance
    vectorized_elements.vacuum_reluctance =  np.zeros((6,total_elements))
    vectorized_elements.minimum_reluctance = np.zeros((6,total_elements)) 
    vectorized_elements.reluctance = np.zeros((6,total_elements)) 

    # permeability
    vectorized_elements.relative_permeability = np.zeros((6,total_elements))

    # flux
    vectorized_elements.flux_direct = np.zeros((6,total_elements))
    vectorized_elements.flux_density_direct = np.zeros((6,total_elements))
    vectorized_elements.flux_density_average = np.zeros((4,total_elements))

    # magnetic_potential
    vectorized_elements.magnetic_potential = reluctance_network.magnetic_potential.data.ravel(order='F')

    for i, element in enumerate(elements.ravel(order = 'F')):
        # material
        if element.material == "magnet":
            vectorized_elements.material[i] = 1
        elif element.material == "iron" :
            vectorized_elements.material[i] = 2
        else:
            vectorized_elements.material[i] = 0

        # dimension  
        vectorized_elements.length[:,i] = element.length.ravel()
        vectorized_elements.section_area[:,i] = element.section_area.ravel()

        # magnetic source 
        vectorized_elements.magnet_source[:,i] = element.magnet_source.ravel()
        vectorized_elements.element_winding_vector[:,i] = element.element_winding_vector.ravel()
        vectorized_elements.winding_source[:,i] = element.winding_source.ravel()
        vectorized_elements.magnetic_source[:,i] = element.magnetic_source.ravel()

        # reluctance
        vectorized_elements.vacuum_reluctance[:,i] = element.vacuum_reluctance.ravel()
        vectorized_elements.minimum_reluctance[:,i] = element.minimum_reluctance.ravel()
        vectorized_elements.reluctance[:,i] = element.reluctance.ravel()

        # permeability
        vectorized_elements.relative_permeability[:,i] = element.relative_permeability.ravel()

        # flux
        vectorized_elements.flux_direct[:,i] = element.flux_direct.ravel()
        vectorized_elements.flux_density_direct[:,i] = element.flux_density_direct.ravel()
        vectorized_elements.flux_density_average[:,i] = element.flux_density_average.ravel()