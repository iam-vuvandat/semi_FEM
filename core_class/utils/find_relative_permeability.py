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
        data = lookup_BH_curve(B_input=element.flux_density_direct, 
                               material_database=element.material_database, 
                               return_du_dB=True)
        relative_permeability = data.mu_r
        d_relative_permeability_d_B = data.dmu_r_dB

    elif element.material == "magnet":
        relative_permeability.fill(element.material_database.magnet.relative_permeance)

    return Output(relative_permeability=relative_permeability,
                  d_relative_permeability_d_B=d_relative_permeability_d_B)