from dataclasses import dataclass
from turtle import position
from typing import Any
import numpy as np


@dataclass
class Output:
    own_magnetic_potential: Any

def find_own_magnetic_potential(element):
    own_magnetic_potential = None

    if  element.magnetic_potential is not None:
        own_magnetic_potential = element.magnetic_potential.retrieve(position = element.position).value
    
    return Output(own_magnetic_potential= own_magnetic_potential)
