from dataclasses import dataclass
from typing import Any
import numpy as np
import scipy.sparse as sp
from tqdm import tqdm

@dataclass
class Output:
    G: Any
    J: Any

def create_magnetic_potential_equation(reluctance_network,
                                       first_time=False,
                                       debug=True):
    if first_time:
        reluctance_network.set_reluctance_at_zero()
        reluctance_network.magnetic_potential.data *= 0 

    mesh = reluctance_network.mesh
    matrix_size = mesh.total_cells - 1
    elements = reluctance_network.elements
    ref_position = elements[-1, -1, -1].position
    
    row_indices = []
    col_indices = []
    values = []
    J = np.zeros(matrix_size)

    iterator = range(matrix_size)
    if debug:
        iterator = tqdm(iterator, desc="Creating Matrix Equation")

    for i_th in iterator:
        i, j_coord, k = reluctance_network.magnetic_potential.get_3D_index(position=i_th).three_dimension_index
        element_center = elements[i, j_coord, k]
        neighbor_elements = element_center.neighbor_elements()

        diag_val = 0.0
        j_val = 0.0

        for m in [0, 1]:
            if m == 0:
                nei_idx = 0
                my_face = 0
                nei_face = 1
                direction = 1.0 
            else:
                nei_idx = 1
                my_face = 1
                nei_face = 0
                direction = -1.0

            for n in [0, 1, 2]:
                element_nei = neighbor_elements[nei_idx, n]
                
                if element_nei is not None:
                    f = element_nei.magnetic_source[nei_face, n] + element_center.magnetic_source[my_face, n]
                    r = element_nei.reluctance[nei_face, n] + element_center.reluctance[my_face, n]
                    
                    conductance = 1.0 / r
                    diag_val += conductance
                    
                    j_val += (f / r) * direction

                    if element_nei.position != ref_position:
                        row_indices.append(i_th)
                        col_indices.append(element_nei.flat_position)
                        values.append(-conductance)

        row_indices.append(i_th)
        col_indices.append(i_th)
        values.append(diag_val)
        J[i_th] = j_val

    G = sp.csr_matrix((values, (row_indices, col_indices)), shape=(matrix_size, matrix_size))

    return Output(G=G, J=J)