from dataclasses import dataclass
from typing import Any
import numpy as np
import scipy.sparse as sp
from tqdm import tqdm

@dataclass
class Output:
    R: Any # Ma trận từ dẫn
    F: Any # Ma trận nguồn sức từ động 
    Ja: Any # Ma trận Jacobian 

def create_loop_flux_equation(reluctance_network,
                              load_factor = 1.0,
                              create_jacobian = False,
                              debug = True):
    