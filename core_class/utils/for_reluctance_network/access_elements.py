from dataclasses import dataclass
from typing import Any

@dataclass
class ElementAccess:
    value: Any
    valid: Any

def access_elements(reluctance_network,
                    position):
    
    # position = (r_i, t_j, z_k)
    
    elements = reluctance_network.elements
    nr,nt,nz = elements.shape
    periodic_boundary = reluctance_network.mesh.periodic_boundary


    value = None
    valid = False
    if periodic_boundary == True:
        if position[0] < 0 or position[0]>= nr:
            pass
        else:
            if position[2] < 0 or position[2] >= nz:
                pass
            else:
                value = elements[position[0],position[1]%nt, position[2]]
                valid = True
        
    else:
        if position[0] < 0 or position[0]>= nr:
            pass
        else:
            if position[2] < 0 or position[2] >= nz:
                pass
            else:
                if position[1] < 0 or position[1] >= nt:
                    pass
                else:
                    value =  elements[position[0],position[1], position[2]]
                    valid = True


    return ElementAccess(value= value,
                         valid= valid)