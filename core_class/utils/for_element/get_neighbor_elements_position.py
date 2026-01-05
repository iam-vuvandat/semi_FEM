from dataclasses import dataclass
import numpy as np
from typing import Any

@dataclass
class Output:
    neighbor_elements_position: np.ndarray

def get_neighbor_elements_position(element):
    nr, nt, nz = element.magnetic_potential.data.shape
    i, j, k = element.position
    periodic_boundary = getattr(element.mesh, 'periodic_boundary', False)

    neighbor_positions = np.full((2, 3), None, dtype=object)

    if 0 <= i - 1 < nr:
        neighbor_positions[0, 0] = (i - 1, j, k)
    if 0 <= i + 1 < nr:
        neighbor_positions[1, 0] = (i + 1, j, k)

    if periodic_boundary:
        neighbor_positions[0, 1] = (i, (j - 1) % nt, k)
        neighbor_positions[1, 1] = (i, (j + 1) % nt, k)
    else:
        if 0 <= j - 1 < nt:
            neighbor_positions[0, 1] = (i, j - 1, k)
        if 0 <= j + 1 < nt:
            neighbor_positions[1, 1] = (i, j + 1, k)

    if 0 <= k - 1 < nz:
        neighbor_positions[0, 2] = (i, j, k - 1)
    if 0 <= k + 1 < nz:
        neighbor_positions[1, 2] = (i, j, k + 1)

    return Output(neighbor_elements_position=neighbor_positions)