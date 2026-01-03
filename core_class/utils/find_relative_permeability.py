from dataclasses import dataclass
import numpy as np
from material.core.lookup_BH_curve import lookup_BH_curve

@dataclass
class Output:
    relative_permeability: np.ndarray
    d_relative_permeability_d_B: np.ndarray

def find_relative_permeability(element,material_relaxation_factor = 1.0):
    material_database = element.material_database
    mu_g = material_database.air.relative_permeance
    mu_m = material_database.magnet.relative_permeance

    current_relative_permeability = element.relative_permeability
    current_d_relative_permeability_d_B = element.d_relative_permeability_d_B

    new_relative_permeability = np.ones((2, 3))
    new_d_relative_permeability_d_B = np.ones((2, 3))

    if element.material == "iron":
        data = lookup_BH_curve(B_input=element.flux_density_average[-1], 
                               material_database=element.material_database, 
                               return_du_dB=True)
        
        new_relative_permeability *= data.mu_r 
        new_d_relative_permeability_d_B *= data.dmu_r_dB

        relative_permeability = (1 - material_relaxation_factor) * current_relative_permeability + new_relative_permeability * material_relaxation_factor
        d_relative_permeability_d_B = (1 - material_relaxation_factor) * current_d_relative_permeability_d_B + new_d_relative_permeability_d_B * material_relaxation_factor


    elif element.material == "magnet":
        relative_permeability = np.ones((2, 3)) * mu_m
        d_relative_permeability_d_B = np.zeros((2, 3))    
    else:
        relative_permeability = np.ones((2, 3)) * mu_g
        d_relative_permeability_d_B = np.zeros((2, 3))

    return Output(relative_permeability=relative_permeability,
                  d_relative_permeability_d_B=d_relative_permeability_d_B)