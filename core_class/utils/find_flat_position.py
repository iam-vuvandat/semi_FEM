from dataclasses import dataclass
import numpy as np


@dataclass
class Output:
    flat_position :int

def find_flat_position(element):
    flat_position = int(element.magnetic_potential.retrieve(position = element.position).index)
    return Output(flat_position= flat_position)
    