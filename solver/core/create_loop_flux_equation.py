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
    
    # Tiền khai báo
    elements = reluctance_network.elements
    
    loop_flux = reluctance_network.loop_flux
    matrix_size = loop_flux.total_size
    R = [[],[],[]] # row, column, value
    F = np.zeros(matrix_size)

    # Viết các vòng mặt Ort===============================
    # Xác định số lớp r, theta, z
    n_r_layer, n_t_layer, n_z_layer = loop_flux.Ort_size[0], loop_flux.Ort_size[1], loop_flux.Ort_size[2]
    # r tăng nhanh nhất, sau đó đến t, sau đó đến z
    
    for k in range(n_z_layer):
        for j in range(n_t_layer):
            for i in range(n_r_layer):
                # truy cập các phần tử lân cận
                Ea = reluctance_network.access_elements(position = (i+1,j,k)).value
                Eb = reluctance_network.access_elements(position = (i+1,j+1,k)).value
                Ec = reluctance_network.access_elements(position = (i,j+1,k)).value
                Ed = reluctance_network.access_elements(position = (i,j,k)).value
                
                # Truy cập các vòng
                center = loop_flux.access_Ort_plane(z_layer = k,
                                                          position = (i,j))
                
                right = loop_flux.access_Ort_plane(z_layer = k,
                                                          position = (i,j+1))
                
                left = loop_flux.access_Ort_plane(z_layer = k,
                                                          position = (i,j-1))
                
                top = loop_flux.access_Ort_plane(z_layer = k,
                                                          position = (i+1,j))
                
                bottom = loop_flux.access_Ort_plane(z_layer = k,
                                                          position = (i-1,j))
                
                # Gán vòng trung tâm:
                R[0].append(center.flat_index)
                R[1].append(center.flat_index)
                R[2].append(+ Ea.reluctance[0,0] + Ea.reluctance[1,1]
                            + Eb.reluctance[0,1] - Eb.reluctance[0,0]
                            - Ec.reluctance[1,0] - Ec.reluctance[0,1]
                            - Ed.reluctance[1,1] + Ed.reluctance[1,0])
                
                # gán các vòng lân cận:
                if top.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(top.flat_index)
                    R[2].append(- Ea.reluctance[1,1] + Eb.reluctance[0,1])

                if right.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(right.flat_index)
                    R[2].append(+ Eb.reluctance[0,0] + Ec.reluctance[1,0])
                
                if bottom.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(bottom.flat_index)
                    R[2].append(+ Ec.reluctance[0,1] + Ed.reluctance[1,1])

                if left.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(left.flat_index)
                    R[2].append(- Ed.reluctance[1,0] - Ea.reluctance[0,0])

                # gán F: 
                F[center.flat_index] = (+ Ea.magnetic_source[0,0] + Ea.magnetic_source[1,1]
                                        + Eb.magnetic_source[0,1] - Eb.magnetic_source[0,0]
                                        - Ec.magnetic_source[1,0] - Ec.magnetic_source[0,1]
                                        - Ed.magnetic_source[1,1] + Ed.magnetic_source[1,0])
                


    # Viết các vòng mặt Orz===============================
    # Xác định số lớp:
    n_r_layer, n_t_layer, n_z_layer = loop_flux.Orz_size[0], loop_flux.Orz_size[2], loop_flux.Orz_size[1]
    # Thứ tự tăng trong mảng: r>z>t
    
    for j in range(n_t_layer):
        for k in range(n_z_layer):
            for i in range(n_r_layer):
                # Truy cập phần tử lân cận 
                Ea = reluctance_network.access_elements(position = (i,j,k+1)).value
                Eb = reluctance_network.access_elements(position = (i+1,j,k+1)).value
                Ec = reluctance_network.access_elements(position = (i+1,j,k)).value
                Ed = reluctance_network.access_elements(position = (i,j,k)).value

                # Truy cập các vòng 
                center = loop_flux.access_Orz_plane(t_layer = j,
                                                    position = (i,k))
                
                top = loop_flux.access_Orz_plane(t_layer = j,
                                                    position = (i,k+1))
                
                right = loop_flux.access_Orz_plane(t_layer = j,
                                                    position = (i+1,k))

                bottom = loop_flux.access_Orz_plane(t_layer = j,
                                                    position = (i,k-1))
                
                left = loop_flux.access_Orz_plane(t_layer = j,
                                                    position = (i-1,k))
                
                # Gán vòng trung tâm 
                R[0].append(center.flat_index)
                R[1].append(center.flat_index)
                R[2].append(+ Ea.reluctance[0,2] + Ea.reluctance[1,0]
                            + Eb.reluctance[0,0] - Eb.reluctance[0,2]
                            - Ec.reluctance[1,2] - Ec.reluctance[0,0]
                            - Ed.reluctance[1,0] + Ed.reluctance[1,2])
                
                # Gán các vòng lân cận
                # gán các vòng lân cận:
                if top.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(top.flat_index)
                    R[2].append(- Ea.reluctance[1,0] + Eb.reluctance[0,0])

                if right.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(right.flat_index)
                    R[2].append(+ Eb.reluctance[0,2] + Ec.reluctance[1,2])
                
                if bottom.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(bottom.flat_index)
                    R[2].append(+ Ec.reluctance[0,0] + Ed.reluctance[1,0])

                if left.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(left.flat_index)
                    R[2].append(- Ed.reluctance[1,2] - Ea.reluctance[0,2])

                # gán F: 
                F[center.flat_index] = (+ Ea.magnetic_source[0,2] + Ea.magnetic_source[1,0]
                                        + Eb.magnetic_source[0,0] - Eb.magnetic_source[0,2]
                                        - Ec.magnetic_source[1,2] - Ec.magnetic_source[0,0]
                                        - Ed.magnetic_source[1,0] + Ed.magnetic_source[1,2])
                

    # Viết các vòng mặt Otz (chỉ 1 lớp r)
    # Xác định số lớp: 
    n_r_layer, n_t_layer, n_z_layer = loop_flux.Otz_size[2], loop_flux.Otz_size[0], loop_flux.Otz_size[1]
    # Thứ tự tăng trong mảng: t>z>r
    for i in range(n_r_layer):
        for k in range(n_z_layer):
            for j in range(n_t_layer):
                
                # Xác định các phần tử lân cận
                Ea = reluctance_network.access_elements(position = (i,j,k+1)).value
                Eb = reluctance_network.access_elements(position = (i,j+1,k+1)).value
                Ec = reluctance_network.access_elements(position = (i,j+1,k)).value
                Ed = reluctance_network.access_elements(position = (i,j,k)).value

                # Xác định các vòng 
                center = loop_flux.access_Otz_plane(r_layer = i,
                                                    position = (j,k))
                
                top = loop_flux.access_Otz_plane(r_layer = i,
                                                    position = (j,k+1))
                
                right = loop_flux.access_Otz_plane(r_layer = i,
                                                    position = (j+1,k))
                
                bottom = loop_flux.access_Otz_plane(r_layer = i,
                                                    position = (j,k-1))
                
                left = loop_flux.access_Otz_plane(r_layer = i,
                                                    position = (j-1,k))
                
                # Gán vòng trung tâm 
                R[0].append(center.flat_index)
                R[1].append(center.flat_index)
                R[2].append(+ Ea.reluctance[0,2] + Ea.reluctance[1,1]
                            + Eb.reluctance[0,1] - Eb.reluctance[0,2]
                            - Ec.reluctance[1,2] - Ec.reluctance[0,1]
                            - Ed.reluctance[1,1] + Ed.reluctance[1,2])
                
                # gán các vòng lân cận:
                if top.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(top.flat_index)
                    R[2].append(- Ea.reluctance[1,1] + Eb.reluctance[0,1])

                if right.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(right.flat_index)
                    R[2].append(+ Eb.reluctance[0,2] + Ec.reluctance[1,2])
                
                if bottom.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(bottom.flat_index)
                    R[2].append(+ Ec.reluctance[0,1] + Ed.reluctance[1,1])

                if left.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(left.flat_index)
                    R[2].append(- Ed.reluctance[1,2] - Ea.reluctance[0,2])

                # gán F: 
                F[center.flat_index] = (+ Ea.magnetic_source[0,2] + Ea.magnetic_source[1,1]
                                        + Eb.magnetic_source[0,1] - Eb.magnetic_source[0,2]
                                        - Ec.magnetic_source[1,2] - Ec.magnetic_source[0,1]
                                        - Ed.magnetic_source[1,1] + Ed.magnetic_source[1,2])
    
    # Viết 1 vòng global duy nhất tại lớp r = 0, z = 0
    n_t = elements.shape[1]
    global_index = loop_flux.access_global(position = (0,0)).flat_index

    global_value = 0.0
    f_value = 0.0
    
    for j in range (n_t):
        global_value += elements[0,j,0].reluctance[0,1] + elements[0,j,0].reluctance[1,1]
        f_value += elements[0,j,0].magnetic_source[0,1] + elements[0,j,0].magnetic_source[1,1]

        # Xác định đóng góp của 4 vòng nhỏ   
        # 2 vòng ở mặt Ort
        #(1)
        R[0].append(global_index)
        R[1].append(loop_flux.access_Ort_plane(z_layer = 0,
                                               position = (0,j-1)).flat_index)
        R[2].append(-elements[0,j,0].reluctance[0,1])
        #(2)
        R[0].append(global_index)
        R[1].append(loop_flux.access_Ort_plane(z_layer = 0,
                                               position = (0,j)).flat_index)
        R[2].append(-elements[0,j,0].reluctance[1,1])

        # 2 vòng mặt Otz
        #(1)
        R[0].append(global_index)
        R[1].append(loop_flux.access_Otz_plane(r_layer = 0,
                                               position = (j-1,0)).flat_index)
        R[2].append(-elements[0,j,0].reluctance[0,1])      

        #(2)
        R[0].append(global_index)
        R[1].append(loop_flux.access_Otz_plane(r_layer = 0,
                                               position = (j,0)).flat_index)
        R[2].append(-elements[0,j,0].reluctance[1,1])  

    R[0].append(global_index)
    R[1].append(global_index)
    R[2].append(global_value)
    F[global_index] = f_value

    R_sparse = sp.csr_matrix((R[2], (R[0], R[1])), shape=(matrix_size, matrix_size))

    return Output(R = R_sparse,
                  F=F,
                  Ja = None)