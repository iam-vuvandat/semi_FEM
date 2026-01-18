from dataclasses import dataclass
import numpy as np

@dataclass
class Output:
    dimension_ratio : np.ndarray

def find_element_segment_dimension_ratio(element):
    dimension_ratio = np.zeros(3)
    dimension = element.dimension
    for i in range(3):
        if dimension[1,i] == 0:
            dimension_ratio[i] = 1
        else:
            dimension_ratio[i] = dimension[0,i] / dimension[1,i]
    
    return Output(dimension_ratio= dimension_ratio)