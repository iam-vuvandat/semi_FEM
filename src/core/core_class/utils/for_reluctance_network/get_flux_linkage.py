from dataclasses import dataclass
from typing import Any
import numpy as np
from src.core.solver.utils.convert_to_dq import convert_to_dq

@dataclass
class Output:
    """
    Container for the flux linkage calculation results.
    """
    flux_linkage: Any

def get_flux_linkage(reluctance_network):
    poles = reluctance_network.geometry_data.rotor.pole_number 
    current_position = reluctance_network.mechanical.current_position

    elements = reluctance_network.elements.flatten()
    phase_number = elements[0].element_winding_vector.size
    
    psi_total = np.zeros(phase_number)
    
    for element in elements:
        winding_normal = element.winding_normal
        theta = winding_normal[1]
        
        # Tính toán vector tác động dựa trên góc xoay hiện tại
        winding_impact = np.array([winding_normal[0] * np.cos(theta), 
                                   winding_normal[0] * np.sin(theta), 
                                   winding_normal[2]])
        
        # Tính mật độ từ thông trung bình đi qua phần tử
        flux_density = element.flux_direct
        b_average = (flux_density[0] + flux_density[1]) * 0.5
        
        # Tính toán đóng góp từ thông Phi của phần tử
        phi_element = b_average @ winding_impact
        
        # Tích lũy vào tổng từ thông liên kết Psi_total = sum (N * Phi)
        psi_total += element.element_winding_vector * phi_element

    # 5. BIẾN ĐỔI SANG HỆ DQ VÀ ĐỊNH DẠNG ĐẦU RA
    # Tạo vector tạm thời để truyền vào hàm convert_to_dq
    temp_val = np.empty((phase_number + 1, 1))
    temp_val[:-1, 0] = psi_total
    temp_val[-1, 0] = current_position

    # Thực hiện biến đổi Park thuận
    dq_data = convert_to_dq(temp_val, poles, current_position)

    # Định dạng đầu ra: [d, q, Phase_A, ..., Phase_N, Rotor_Position]
    flux_linkage_results = np.empty((phase_number + 3, 1))
    flux_linkage_results[0, 0] = dq_data[0, 0]     # Trục d
    flux_linkage_results[1, 0] = dq_data[1, 0]     # Trục q
    flux_linkage_results[2:-1, 0] = psi_total      # Giá trị các pha
    flux_linkage_results[-1, 0] = current_position # Vị trí cơ học

    return Output(flux_linkage=flux_linkage_results)