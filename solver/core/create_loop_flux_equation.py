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
    R = [[],[],[]]
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
                


    

    # Viết các vòng mặt Orz


    # Viết 1 lớp vòng các vòng mặt Otz


    # Viết 1 vòng global duy nhất