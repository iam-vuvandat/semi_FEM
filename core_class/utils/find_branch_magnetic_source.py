import numpy as np
from dataclasses import dataclass
from typing import Any

@dataclass
class Output:
    branch_magnetic_source: Any

def find_branch_magnetic_source(element):
    average_source = element.magnet_source + element.winding_source
    total_source = average_source[0, :] * 2
    
    k = element.length_ratio
    relative_k = np.vstack([k, 1/k])
    
    branch_magnetic_source = total_source / (1 + 1/relative_k)
    
    return Output(branch_magnetic_source=branch_magnetic_source)