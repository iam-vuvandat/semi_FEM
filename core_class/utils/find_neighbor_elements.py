from dataclasses import dataclass
import numpy as np
from typing import Any

@dataclass
class Output:
    neighbor_elements: Any

def find_neighbor_elements(element):
    neighbor_elements = np.full((2, 3), None, dtype=object)
    neighbor_positions = element.neighbor_elements_position
    elements_matrix = element.elements
    
    for i in range(2):
        for j in range(3):
            position = neighbor_positions[i, j]
            if position is not None:
                neighbor_elements[i, j] = elements_matrix[position]
    
    return Output(neighbor_elements=neighbor_elements)