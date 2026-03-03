from dataclasses import dataclass
from typing import Any
import numpy as np
import scipy.sparse as sp
from tqdm import tqdm

@dataclass
class Output:
    G: Any # Ma trận từ thế
    J: Any # Ma trận nguồn từ thông 

def create_magnetic_potential_equation(reluctance_network,
                                       load_factor=1.0,
                                       debug=True):
    
    mesh = reluctance_network.mesh
    n_elements = mesh.total_cells
    matrix_size = n_elements - 1
    
    # =========================================================================
    # LUỒNG 1: OOP (Dành cho Debug hoặc Lưới nhỏ)
    # =========================================================================
    if reluctance_network.vectorized_optimization is False:
        elements = reluctance_network.elements
        ref_position = elements[-1, -1, -1].position
        
        G_list = [[], [], []]
        J = np.zeros(matrix_size)

        iterator = range(matrix_size)
        if debug:
            iterator = tqdm(iterator, desc="Creating Matrix Equation (OOP)")

        for i_th in iterator:
            idx_3d = reluctance_network.magnetic_potential.get_3D_index(position=i_th).three_dimension_index
            element_center = elements[idx_3d[0], idx_3d[1], idx_3d[2]]
            neighbor_elements = element_center.neighbor_elements()

            diag_val = 0.0
            j_val = 0.0

            for m in [0, 1]:
                # m=0: r-in, t-left, z-bot | m=1: r-out, t-right, z-top
                if m == 0:
                    nei_idx, my_face, nei_face, direction = 0, 0, 1, 1.0 
                else:
                    nei_idx, my_face, nei_face, direction = 1, 1, 0, -1.0

                for n in [0, 1, 2]:
                    element_nei = neighbor_elements[nei_idx, n]
                    
                    if element_nei is not None:
                        f = (element_center.magnetic_source[my_face, n] + element_nei.magnetic_source[nei_face, n]) * load_factor
                        r = element_center.reluctance[my_face, n] + element_nei.reluctance[nei_face, n]
                        conductance = 1.0 / r

                        diag_val += conductance
                        j_val += (f / r) * direction

                        if element_nei.position != ref_position:
                            G_list[0].append(i_th)
                            G_list[1].append(element_nei.flat_position)
                            G_list[2].append(-conductance)

            G_list[0].append(i_th)
            G_list[1].append(i_th)
            G_list[2].append(diag_val)
            J[i_th] = j_val

        G_sparse = sp.csr_matrix((G_list[2], (G_list[0], G_list[1])), shape=(matrix_size, matrix_size))
        return Output(G=G_sparse, J=J)

    # =========================================================================
    # LUỒNG 2: VECTORIZED (Dành cho hiệu năng cao)
    # =========================================================================
    else:
        ve = reluctance_network.vectorized_elements
        
        # 1. Quy ước hướng đối diện và hướng nguồn
        # 0:r-in, 1:t-left, 2:z-bot | 3:r-out, 4:t-right, 5:z-top
        opp_face = np.array([3, 4, 5, 0, 1, 2])
        directions = np.array([1.0, 1.0, 1.0, -1.0, -1.0, -1.0])
        
        # 2. Lấy dữ liệu từ láng giềng bằng Fancy Indexing
        # r_neighbor[k, i] là reluctance tại mặt đối diện của láng giềng thứ k của phần tử i
        r_neighbor = ve.reluctance[opp_face[:, None], ve.neighbor_indices]
        f_neighbor = ve.magnetic_source[opp_face[:, None], ve.neighbor_indices]
        
        # 3. Tính toán thông số nhánh đồng loạt
        r_total = ve.reluctance + r_neighbor
        f_total = (ve.magnetic_source + f_neighbor) * load_factor
        conductance = 1.0 / r_total
        
        # 4. Xây dựng Vector nguồn J (loại bỏ nút gốc cuối cùng)
        # J = sum( (F/R) * direction * mask )
        j_all = np.sum((f_total / r_total) * directions[:, None] * ve.neighbor_valid, axis=0)
        J_vec = j_all[:matrix_size]
        
        # 5. Xây dựng Ma trận G (COO format)
        # Tính đường chéo: Tổng conductance của các nhánh hợp lệ
        diag_values = np.sum(conductance * ve.neighbor_valid, axis=0)[:matrix_size]
        
        rows, cols, data = [], [], []
        
        # Thêm đường chéo chính
        rows.append(np.arange(matrix_size))
        cols.append(np.arange(matrix_size))
        data.append(diag_values)
        
        # Thêm các phần tử ngoài đường chéo cho 6 hướng láng giềng
        for k in range(6):
            i_idx = np.arange(matrix_size)
            j_idx = ve.neighbor_indices[k, :matrix_size]
            
            # Điều kiện: Láng giềng tồn tại VÀ không phải là nút gốc (index < matrix_size)
            mask = ve.neighbor_valid[k, :matrix_size] & (j_idx < matrix_size)
            
            rows.append(i_idx[mask])
            cols.append(j_idx[mask])
            data.append(-conductance[k, :matrix_size][mask])
            
        G_sparse = sp.csr_matrix((np.concatenate(data), 
                                 (np.concatenate(rows), np.concatenate(cols))), 
                                 shape=(matrix_size, matrix_size))
        
        return Output(G=G_sparse, J=J_vec)