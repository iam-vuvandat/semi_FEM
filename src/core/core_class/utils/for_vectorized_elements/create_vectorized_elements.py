import numpy as np 

def create_vectorized_elements(vectorized_elements,reluctance_network):
    elements = reluctance_network.elements
    total_elements = elements.size

    # material
    vectorized_elements.material = np.zeros(total_elements)

    # dimension
    vectorized_elements.length   = np.zeros((6,total_elements))
    vectorized_elements.section_area = np.zeros((6,total_elements))

    # magnetic source
    vectorized_elements.magnet_source = np.zeros((6,total_elements))
    vectorized_elements.element_winding_vector = np.zeros((6,total_elements))

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



