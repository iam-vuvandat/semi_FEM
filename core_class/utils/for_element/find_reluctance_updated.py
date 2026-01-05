from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass
class Output:
    reluctance : np.ndarray

def find_reluctance_updated(element):
    reluctance = element.vacuum_reluctance / element.relative_permeability

    return Output(reluctance= reluctance)