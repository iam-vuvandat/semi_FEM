import numpy as np 
import math 
from dataclasses import dataclass
from typing import Any

pi = math.pi

@dataclass
class Output:
    reluctance: Any

def find_vacuum_reluctance(length, section_area):
    mu_0 = 4 * pi * 1e-7
    reluctance = length / (mu_0 * section_area)
    return Output(reluctance=reluctance)