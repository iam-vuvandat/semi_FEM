from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass
class Output:
    flux_density_direct: np.ndarray
    flux_density_average: np.ndarray

def find_flux_density(element):
    flux_direct = element.flux_direct
    section_area = element.section_area

    flux_density_direct = flux_direct / section_area

    flux_sum = np.sum(flux_direct, axis=0)
    area_sum = np.sum(section_area, axis=0)
    
    b_components = flux_sum / area_sum
    b_mag = np.sqrt(np.sum(b_components**2))

    flux_density_average = np.append(b_components, b_mag)

    return Output(flux_density_direct=flux_density_direct,
                  flux_density_average=flux_density_average)