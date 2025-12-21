from dataclasses import dataclass
import numpy as np
from material.core.lookup_BH_curve import lookup_BH_curve

@dataclass
class Output:
    relative_permeability: np.ndarray
    d_relative_permeability_d_B: np.ndarray

def find_relative_permeability(element):
    relative_permeability = np.ones((2, 3))
    d_relative_permeability_d_B = np.zeros((2, 3))
    
    if element.material == "iron":
        flux_density = element.flux_density_direct
        material_db = element.material_database
        
        for i in range(2):
            for j in range(3):
                data = lookup_BH_curve(B_input=flux_density[i, j], 
                                       material_database=material_db, 
                                       return_du_dB=True)
                relative_permeability[i, j] = data.mu_r
                d_relative_permeability_d_B[i, j] = data.dmu_r_dB

    elif element.material == "magnet":
        relative_permeability.fill(element.material_database.magnet.relative_permeance)

    return Output(relative_permeability=relative_permeability,
                  d_relative_permeability_d_B=d_relative_permeability_d_B)