from dataclasses import dataclass
from typing import Any
import numpy as np
import scipy.sparse as sp
from tqdm import tqdm

@dataclass
class Output:
    G: Any
    J: Any
    Ja: Any

def create_magnetic_potential_equation(reluctance_network,
                                       first_time=False,
                                       load_factor=1.0,
                                       debug=True):
    if first_time:
        reluctance_network.set_reluctance_at_zero()
        reluctance_network.magnetic_potential.data *= 0 

    mesh = reluctance_network.mesh
    matrix_size = mesh.total_cells - 1
    elements = reluctance_network.elements
    ref_position = elements[-1, -1, -1].position
    
    G = [[], [], []]
    J = np.zeros(matrix_size)

    iterator = range(matrix_size)
    if debug:
        iterator = tqdm(iterator, desc="Creating Matrix Equation")

    for i_th in iterator:
        idx_3d = reluctance_network.magnetic_potential.get_3D_index(position=i_th).three_dimension_index
        element_center = elements[idx_3d[0], idx_3d[1], idx_3d[2]]
        neighbor_elements = element_center.neighbor_elements()

        diag_val = 0.0
        j_val = 0.0

        for m in [0, 1]:
            if m == 0:
                nei_idx, my_face, nei_face, direction = 0, 0, 1, 1.0 
            else:
                nei_idx, my_face, nei_face, direction = 1, 1, 0, -1.0

            for n in [0, 1, 2]:
                element_nei = neighbor_elements[nei_idx, n]
                
                if element_nei is not None:
                    f = (element_nei.magnetic_source[nei_face, n] + element_center.magnetic_source[my_face, n]) * load_factor
                    r = element_nei.reluctance[nei_face, n] + element_center.reluctance[my_face, n]
                    conductance = 1.0 / r

                    diag_val += conductance
                    j_val += (f / r) * direction

                    if element_nei.position != ref_position:
                        G[0].append(i_th)
                        G[1].append(element_nei.flat_position)
                        G[2].append(-conductance)
                        
        G[0].append(i_th)
        G[1].append(i_th)
        G[2].append(diag_val)
        J[i_th] = j_val

    G_sparse = sp.csr_matrix((G[2], (G[0], G[1])), shape=(matrix_size, matrix_size))

    return Output(G=G_sparse, J=J, Ja=None)