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
    
    Ja = [[], [], []]
    G = [[], [], []]
    J = np.zeros(matrix_size)

    iterator = range(matrix_size)
    if debug:
        iterator = tqdm(iterator, desc="Creating Matrix Equation")

    for i_th in iterator:
        i, j, k_idx = reluctance_network.magnetic_potential.get_3D_index(position=i_th).three_dimension_index
        element_center = elements[i, j, k_idx]
        neighbor_elements = element_center.neighbor_elements()

        diag_val = 0.0
        ja_diag_val = 0.0
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
                    
                    # Tính K (Độ nhạy bão hòa - S bậc 1)
                    ka = (-element_center.reluctance[my_face, n] / element_center.relative_permeability[my_face, n]) * \
                         (1.0 / element_center.section_area[my_face, n]) * \
                         element_center.d_relative_permeability_d_B[my_face, n]
                    kb = (-element_nei.reluctance[nei_face, n] / element_nei.relative_permeability[nei_face, n]) * \
                         (1.0 / element_nei.section_area[nei_face, n]) * \
                         element_nei.d_relative_permeability_d_B[nei_face, n]
                    k_total = ka + kb

                    # Tính U hiệu dụng đồng nhất với direction
                    u_eff = (element_center.own_magnetic_potential - element_nei.own_magnetic_potential) * (-direction) - f
                    
                    # Jacobian giải tích: ja_val = R / (R^2 - K*U)
                    ja_val = r / (r**2 - k_total * u_eff)

                    diag_val += conductance
                    ja_diag_val += ja_val
                    j_val += (f / r) * direction

                    if element_nei.position != ref_position:
                        G[0].append(i_th)
                        G[1].append(element_nei.flat_position)
                        G[2].append(-conductance)

                        Ja[0].append(i_th)
                        Ja[1].append(element_nei.flat_position)
                        Ja[2].append(-ja_val)
                        
        G[0].append(i_th)
        G[1].append(i_th)
        G[2].append(diag_val)
        
        J[i_th] = j_val

        Ja[0].append(i_th)
        Ja[1].append(i_th)
        Ja[2].append(ja_diag_val)

    G_sparse = sp.csr_matrix((G[2], (G[0], G[1])), shape=(matrix_size, matrix_size))
    Ja_sparse = sp.csr_matrix((Ja[2], (Ja[0], Ja[1])), shape=(matrix_size, matrix_size))

    return Output(G=G_sparse, J=J, Ja=Ja_sparse)