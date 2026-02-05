from dataclasses import dataclass
from typing import Any
import numpy as np
import scipy.sparse as sp
from tqdm import tqdm

@dataclass
class Output:
    G: Any # Ma trận từ thế
    J: Any # Ma trận nguồn từ thông 
    Ja: Any # Ma trận Jacobian 

def create_magnetic_potential_equation(reluctance_network,
                                       load_factor=1.0,
                                       debug=True):
    
    mesh = reluctance_network.mesh
    matrix_size = mesh.total_cells - 1
    elements = reluctance_network.elements
    ref_position = elements[-1, -1, -1].position
    
    G = [[], [], []]
    Ja = [[],[],[]]
    J = np.zeros(matrix_size)

    iterator = range(matrix_size)
    if debug:
        iterator = tqdm(iterator, desc="Creating Matrix Equation")

    for i_th in iterator:
        idx_3d = reluctance_network.magnetic_potential.get_3D_index(position=i_th).three_dimension_index
        element_center = elements[idx_3d[0], idx_3d[1], idx_3d[2]]
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
                    
                    f_center = element_center.magnetic_source[my_face, n] * load_factor
                    f_neighbor = element_nei.magnetic_source[nei_face, n] * load_factor
                    f = f_center + f_neighbor

                    r_center = element_center.reluctance[my_face, n]
                    r_neighbor = element_nei.reluctance[nei_face, n]
                    r = r_center + r_neighbor
                    conductance = 1.0 / r
                    conductance2 = conductance * conductance

                    mu_center = element_center.relative_permeability[my_face, n]
                    mu_neighbor = element_nei.relative_permeability[nei_face, n]

                    dmu_center = element_center.d_relative_permeability_d_B[my_face, n]
                    dmu_neighbor = element_nei.d_relative_permeability_d_B[nei_face, n]

                    S_center = element_center.section_area[my_face, n]
                    S_neighbor = element_nei.section_area[nei_face, n]


                    diag_val += conductance
                    j_val += (f / r) * direction

                    ####
                    K1 = (-r_center / mu_center) * (1/S_center) * dmu_center
                    K2 = (-r_neighbor / mu_neighbor) * (1/S_neighbor) * dmu_neighbor
                    K = K1 + K2

                    Pc = element_center.own_magnetic_potential
                    Pn = element_nei.own_magnetic_potential
                    U = (Pc-Pn) * (-direction) + f

                    C = conductance2 * ((K*direction*r)/(conductance2-K*U)) * (Pn-Pc)
                    ja_diag_val -=C

                    if element_nei.position != ref_position:
                        G[0].append(i_th)
                        G[1].append(element_nei.flat_position)
                        G[2].append(-conductance)

                        Ja[0].append(i_th)
                        Ja[1].append(element_nei.flat_position)
                        Ja[2].append(C-conductance)

                        
        G[0].append(i_th)
        G[1].append(i_th)
        G[2].append(diag_val)
        J[i_th] = j_val

        Ja[0].append(i_th)
        Ja[1].append(i_th)
        Ja[2].append(ja_diag_val + diag_val)

    G_sparse = sp.csr_matrix((G[2], (G[0], G[1])), shape=(matrix_size, matrix_size))
    Ja_sparse = sp.csr_matrix((Ja[2], (Ja[0], Ja[1])), shape=(matrix_size, matrix_size))

    return Output(G=G_sparse, J=J , Ja = Ja_sparse)