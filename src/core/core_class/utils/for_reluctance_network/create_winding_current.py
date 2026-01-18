import numpy as np 

def create_winding_current(reluctance_network):
    number_of_phase = reluctance_network.geometry.geometry[0].winding_vector.size
    return np.zeros(number_of_phase)    