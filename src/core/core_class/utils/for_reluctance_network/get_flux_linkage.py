from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass
class Output:
    flux_linkage: Any

def get_flux_linkage(reluctance_network):
    use_symmetry = reluctance_network.mesh.detail_parameter[-2]
    m_factor = reluctance_network.symmetry_factor if use_symmetry else 1.0

    elements = reluctance_network.elements.flatten()
    phase_number = elements[0].element_winding_vector.size
    
    psi_total = np.zeros(phase_number)
    
    for element in elements:
        w_n = element.winding_normal
        theta = w_n[1]
        
        w_impact = np.array([w_n[0] * np.cos(theta), 
                             w_n[0] * np.sin(theta), 
                             w_n[2]])
        
        f_d = element.flux_direct
        b_avg = (f_d[0] + f_d[1]) * 0.5
        
        phi_element = b_avg @ w_impact
        
        psi_total += element.element_winding_vector * phi_element

    flux_linkage = np.empty((phase_number + 1, 1))
    flux_linkage[:-1, 0] = psi_total * m_factor
    flux_linkage[-1] = reluctance_network.current_position

    return Output(flux_linkage=flux_linkage)