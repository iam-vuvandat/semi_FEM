from dataclasses import dataclass
from typing import Any
import numpy as np

from material.core.lookup_BH_curve import lookup_BH_curve
@dataclass
class Output:
    relative_permeability : np.ndarray

def find_relative_permeability(element):
    relative_permeability = np.ones((2,3))
    material_database = element.material_database

    if element.material == "iron":
        for i in range(2):
            for j in range(3):
                relative_permeability[i,j] = lookup_BH_curve(B_input= element.flux_density_direct[i,j],
                                                        material_database= material_database).mu_r
                
    else:
        if element.material == "magnet":
           relative_permeability = np.full((2, 3), material_database.magnet.relative_permeance)
        elif element.material == "air":
            relative_permeability = np.full((2, 3), 1)
    return Output(relative_permeability=relative_permeability)