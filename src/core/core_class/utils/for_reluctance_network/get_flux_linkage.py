from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass
class Output:
    """
    Container for the flux linkage calculation results.
    """
    flux_linkage: Any

def get_flux_linkage(reluctance_network):
    """
    Calculates the total flux linkage for all phases based on the current magnetic state.
    Updated to use the refactored adaptive_mesh_data structure.
    """
    # 1. Access the refactored adaptive_mesh_data container
    # Replacing the legacy list access mesh.detail_parameter[-2]
    mesh_data = reluctance_network.mesh.adaptive_mesh_data
    use_symmetry = mesh_data.use_symmetry_factor
    
    # 2. Determine the multiplier based on the symmetry factor
    # If using symmetry, we scale the partial flux to represent the full machine
    machine_factor = reluctance_network.symmetry_factor if use_symmetry else 1.0

    # 3. Analyze elements to determine the number of phases
    elements = reluctance_network.elements.flatten()
    phase_number = elements[0].element_winding_vector.size
    
    # Initialize total flux linkage for each phase
    psi_total = np.zeros(phase_number)
    
    # 4. Integrate flux linkage across all elements
    for element in elements:
        # Get winding normal orientation (Radial, Theta, Axial)
        winding_normal = element.winding_normal
        theta = winding_normal[1]
        
        # Calculate the impact vector based on current rotation
        # Logic remains strictly identical to original geometric projection
        winding_impact = np.array([winding_normal[0] * np.cos(theta), 
                                   winding_normal[0] * np.sin(theta), 
                                   winding_normal[2]])
        
        # Calculate average flux density through the element
        flux_density = element.flux_direct
        b_average = (flux_density[0] + flux_density[1]) * 0.5
        
        # Compute element flux contribution
        phi_element = b_average @ winding_impact
        
        # Accumulate to total phase flux linkage
        psi_total += element.element_winding_vector * phi_element

    # 5. Format output: [Phase_A, Phase_B, Phase_C, Rotor_Position]
    # Creating a column vector to store linkage and current angular position
    flux_linkage_results = np.empty((phase_number + 1, 1))
    flux_linkage_results[:-1, 0] = psi_total * machine_factor
    flux_linkage_results[-1] = reluctance_network.current_position

    return Output(flux_linkage=flux_linkage_results)