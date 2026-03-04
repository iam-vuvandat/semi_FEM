from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass
class Output:
    """
    Container for the flux linkage calculation results.
    """
    flux_linkage: Any

def get_flux_linkage(reluctance_network):
    """
    Calculates the total flux linkage for all phases based on the current magnetic state.
    Strictly follows the refactored original variable names.
    """
    
    elements = reluctance_network.elements.flatten()
    # Lấy số lượng pha từ kích thước của winding vector trong phần tử
    phase_number = elements[0].element_winding_vector.size
    
    # Khởi tạo tổng từ thông liên kết $\Psi$ cho từng pha
    psi_total = np.zeros(phase_number)
    
    # 4. TÍCH PHÂN TỪ THÔNG TRÊN TOÀN BỘ PHẦN TỬ
    for element in elements:
        winding_normal = element.winding_normal
        theta = winding_normal[1]
        
        winding_impact = np.array([winding_normal[0] * np.cos(theta), 
                                   winding_normal[0] * np.sin(theta), 
                                   winding_normal[2]])
        
        flux_density = element.flux_direct
        b_average = (flux_density[0] + flux_density[1]) * 0.5
        
        # Tính toán đóng góp từ thông $\Phi$ của phần tử
        phi_element = b_average @ winding_impact
        
        # Tích lũy vào tổng từ thông liên kết $\Psi_{total} = \sum (N \cdot \Phi)$
        psi_total += element.element_winding_vector * phi_element

    # 5. ĐỊNH DẠNG ĐẦU RA: [Phase_A, Phase_B, Phase_C, Rotor_Position]
    # Tạo vector cột để lưu kết quả và vị trí góc hiện tại của rotor
    flux_linkage_results = np.empty((phase_number + 1, 1))
    #flux_linkage_results[:-1, 0] = psi_total * machine_factor
    flux_linkage_results[-1] = reluctance_network.mechanical.current_position

    return Output(flux_linkage=flux_linkage_results)