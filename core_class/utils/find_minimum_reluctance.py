from dataclasses import dataclass
from typing import Any
from material.utils.find_maximum_permeance import find_maximum_permeance

@dataclass
class Output:
    reluctance: Any

def find_minimum_reluctance(element):
    reluctance = element.vacuum_reluctance
    
    if element.material == "magnet":
        material_database = element.material_database
        maximum_permeance = material_database.magnet.relative_permeance
        reluctance = reluctance * 1/maximum_permeance

    elif element.material == "iron":
        material_database = element.material_database
        maximum_permeance = find_maximum_permeance(material_database=material_database).mu_r_max
        reluctance = reluctance * 1/maximum_permeance

    return Output(reluctance= reluctance)
