from dataclasses import dataclass
from material.core.lookup_BH_curve import lookup_BH_curve

@dataclass
class Output:
    permeability : float

def find_permeability_at_zero(material_database):
    permeability = lookup_BH_curve(B_input= 0.0,
                                   material_database= material_database,
                                   return_du_dB=False).mu_r
    
    return Output(permeability= permeability)
