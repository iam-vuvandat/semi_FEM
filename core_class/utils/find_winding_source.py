from dataclasses import dataclass
import numpy as np

@dataclass
class Output:
    element_winding_vector : np.ndarray
    winding_source :np.ndarray

def find_winding_source(element) :
    """
    Trong các động cơ dọc trục, dây quấn luôn quấn với pháp tuyến song song trục z
    """

    if element.element_winding_vector is None:
        element_winding_vector = element.segment_winding_vector * element.dimension_ratio[-1]

    else:
        element_winding_vector = element.element_winding_vector
    
    winding_source = np.zeros((2,3))
    F = element.winding_current @ element_winding_vector 
    winding_source[0,-1] = F/2
    winding_source[1,-1] = F/2

    return Output(element_winding_vector= element_winding_vector,
                  winding_source= winding_source)