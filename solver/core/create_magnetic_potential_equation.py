from dataclasses import dataclass
from typing import Any
import numpy as np
import scipy.sparse as sp
from tqdm import tqdm

@dataclass
class Output:
    G: Any           # Ma trận độ dẫn (Picard/Linear)
    J: Any           # Vector nguồn (Source vector)
    Ja: Any          # Ma trận Jacobian Giải tích (Analytic)
    Ja_numeric: Any  # Ma trận Jacobian Số trị (Numerical) - Trả về None nếu không yêu cầu

def create_magnetic_potential_equation(reluctance_network,
                                       load_factor=1.0,
                                       compute_numeric=True,
                                       debug=True):
    
    mesh = reluctance_network.mesh
    matrix_size = mesh.total_cells - 1
    elements = reluctance_network.elements
    ref_position = elements[-1, -1, -1].position
    
    # Khởi tạo danh sách cho ma trận thưa
    G_data = [[], [], []]   # [row, col, data]
    Ja_data = [[], [], []]  # [row, col, data]
    J_vec = np.zeros(matrix_size)

    iterator = range(matrix_size)
    if debug:
        iterator = tqdm(iterator, desc="Assembling Matrices", leave=False)

    # --- BƯỚC 1: LẮP GHÉP G, J VÀ JA GIẢI TÍCH ---
    for i_th in iterator:
        idx_3d = reluctance_network.magnetic_potential.get_3D_index(position=i_th).three_dimension_index
        element_center = elements[idx_3d[0], idx_3d[1], idx_3d[2]]
        neighbor_elements = element_center.neighbor_elements()

        diag_val = 0.0
        ja_diag_val = 0.0
        j_val = 0.0

        for m in [0, 1]:
            nei_idx, my_face, nei_face, direction = (0, 0, 1, 1.0) if m == 0 else (1, 1, 0, -1.0)

            for n in [0, 1, 2]:
                element_nei = neighbor_elements[nei_idx, n]
                if element_nei is not None:
                    # Sức từ động (MMF)
                    f = (element_center.magnetic_source[my_face, n] + element_nei.magnetic_source[nei_face, n]) * load_factor

                    # Độ dẫn từ
                    r = element_center.reluctance[my_face, n] + element_nei.reluctance[nei_face, n]
                    conductance = 1.0 / r
                    
                    # Thành phần đạo hàm (Jacobian)
                    mu_c = element_center.relative_permeability[my_face, n]
                    mu_n = element_nei.relative_permeability[nei_face, n]
                    S_c = element_center.section_area[my_face, n]
                    S_n = element_nei.section_area[nei_face, n]
                    
                    dmu_dB_c = element_center.d_relative_permeability_d_B[my_face, n]
                    dmu_dB_n = element_nei.d_relative_permeability_d_B[nei_face, n]

                    # Công thức đạo hàm Jacobian (C)
                    U = (element_center.own_magnetic_potential - element_nei.own_magnetic_potential) * direction - f
                    k1 = (-element_center.reluctance[my_face, n] / (mu_c * S_c)) * dmu_dB_c
                    k2 = (-element_nei.reluctance[nei_face, n] / (mu_n * S_n)) * dmu_dB_n
                    K = k1 + k2
                    
                    # Tránh chia cho 0 tại vùng bão hòa gắt
                    denom = (conductance**2 - (K * U))
                    C = - (conductance**2) * ((K * direction * r) / (denom if abs(denom) > 1e-15 else 1e-15)) * \
                        (element_center.own_magnetic_potential - element_nei.own_magnetic_potential)
                    
                    diag_val += conductance
                    ja_diag_val -= C
                    j_val += (f / r) * direction

                    if element_nei.position != ref_position:
                        # Ma trận G (Picard)
                        G_data[0].append(i_th); G_data[1].append(element_nei.flat_position); G_data[2].append(-conductance)
                        # Ma trận Ja (Newton)
                        Ja_data[0].append(i_th); Ja_data[1].append(element_nei.flat_position); Ja_data[2].append(C - conductance)

        # Chèn phần tử đường chéo
        G_data[0].append(i_th); G_data[1].append(i_th); G_data[2].append(diag_val)
        Ja_data[0].append(i_th); Ja_data[1].append(i_th); Ja_data[2].append(ja_diag_val + diag_val)
        J_vec[i_th] = j_val

    # Chuyển sang ma trận thưa CSR
    G_sparse = sp.csr_matrix((G_data[2], (G_data[0], G_data[1])), shape=(matrix_size, matrix_size))
    Ja_sparse = sp.csr_matrix((Ja_data[2], (Ja_data[0], Ja_data[1])), shape=(matrix_size, matrix_size))

    # --- BƯỚC 2: TÍNH TOÁN JACOBIAN SỐ TRỊ (NẾU YÊU CẦU) ---
    Ja_numeric = None
    if compute_numeric:
        if debug: print(f"\n\033[93m[!] Calculating Numerical Jacobian (Finite Difference)...\033[0m")
        epsilon = 1e-7
        p_orig = reluctance_network.magnetic_potential.data.flatten(order='F')[:-1]
        
        # Hàm tính Residual F(P) = G*P - J
        def get_residual(p_in):
            reluctance_network.magnetic_potential.data = np.append(p_in, 0.0).reshape(reluctance_network.magnetic_potential.data.shape, order='F')
            reluctance_network.update_reluctance_network()
            # Gọi đệ quy chế độ cơ bản để lấy G và J
            temp_out = create_magnetic_potential_equation(reluctance_network, load_factor, False, False)
            return temp_out.G.dot(p_in) - temp_out.J

        f0 = get_residual(p_orig)
        Ja_num_lil = Ja_sparse.tolil() # Dùng cấu trúc thưa của Ja_analytic để tối ưu

        for j in range(matrix_size):
            p_perturbed = p_orig.copy()
            p_perturbed[j] += epsilon
            f_perturbed = get_residual(p_perturbed)
            
            # Đạo hàm cột j
            col_diff = (f_perturbed - f0) / epsilon
            
            # Chỉ cập nhật các hàng i mà cấu trúc thưa cho phép
            rows = Ja_sparse.getrow(j).indices
            for i in rows:
                Ja_num_lil[i, j] = col_diff[i]
        
        Ja_numeric = Ja_num_lil.tocsr()

    return Output(G=G_sparse, J=J_vec, Ja=Ja_sparse, Ja_numeric=Ja_numeric)