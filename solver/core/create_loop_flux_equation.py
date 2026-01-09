from dataclasses import dataclass
from turtle import position
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

    # Viết các vòng mặt Ort
    # Xác định số lớp z:
    n_z_layer = loop_flux.Ort_size[2]
    # Xác định số lớp r, theta
    n_r_layer, n_t_layer, n_z_layer = loop_flux.Ort_size[0], loop_flux.Ort_size[1], loop_flux.Ort_size[2]
    # r tăng nhanh nhất, sau đó đến t, sau đó đến z
    
    for k in range(n_z_layer):
        for j in range(n_t_layer):
            for i in range(n_r_layer):
                # truy cập các phần tử lân cận
                Ea = reluctance_network.access_elements(position = (i+1,j,k))
                Eb = reluctance_network.access_elements(position = (i+1,j+1,k))
                Ec = reluctance_network.access_elements(position = (i,j+1,k))
                Ed = reluctance_network.access_elements(position = (i,j,k))
                
                # Truy cập các vòng
                center = loop_flux.access_Ort_plane(n_z_layer = k,
                                                          position = (i,j))
                
                right = loop_flux.access_Ort_plane(n_z_layer = k,
                                                          position = (i,j+1))
                
                left = loop_flux.access_Ort_plane(n_z_layer = k,
                                                          position = (i,j-1))
                
                top = loop_flux.access_Ort_plane(n_z_layer = k,
                                                          position = (i+1,j))
                
                bottom = loop_flux.access_Ort_plane(n_z_layer = k,
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
                    R[2].append(+ Ec.reluctane[0,1] + Ed.reluctance[1,1])

                if left.valid is True:
                    R[0].append(center.flat_index)
                    R[1].append(left.flat_index)
                    R[2].append(- Ed.reluctance[1,0] - Ea.reluctance[0,0])

                # gán F: 
                F[center.flat_index] = (+ Ea.magnetic_source[0,0] + Ea.magnetic_source[1,1]
                                        + Eb.magnetic_source[0,1] - Eb.magnetic_source[0,0]
                                        - Ec.magnetic_source[1,0] - Ec.magnetic_source[0,1]
                                        - Ed.magnetic_source[1,1] + Ed.magnetic_source[1,0])
                



    

    # Viết các vòng mặt Orz


    # Viết 1 lớp vòng các vòng mặt Otz


    # Viết 1 vòng global duy nhất