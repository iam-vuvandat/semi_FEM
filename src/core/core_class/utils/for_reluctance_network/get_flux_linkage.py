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
    # 1. TRUY XUẤT DỮ LIỆU TỪ MESH CONTAINER
    # Truy cập trực tiếp vào adaptive_mesh_data của motor
    mesh_data = reluctance_network.mesh.adaptive_mesh_data
    use_symmetry = mesh_data.use_symmetry_factor
    
    # 2. XÁC ĐỊNH HỆ SỐ MÁY ĐIỆN
    # Lấy symmetry_factor trực tiếp từ motor để đảm bảo tính đồng bộ
    machine_factor = reluctance_network.symmetry_factor if use_symmetry else 1.0

    # 3. PHÂN TÍCH PHẦN TỬ ĐỂ XÁC ĐỊNH SỐ PHA
    elements = reluctance_network.elements.flatten()
    # Lấy số lượng pha từ kích thước của winding vector trong phần tử
    phase_number = elements[0].element_winding_vector.size
    
    # Khởi tạo tổng từ thông liên kết $\Psi$ cho từng pha
    psi_total = np.zeros(phase_number)
    
    # 4. TÍCH PHÂN TỪ THÔNG TRÊN TOÀN BỘ PHẦN TỬ
    for element in elements:
        # Lấy vector pháp tuyến của dây quấn (Radial, Theta, Axial)
        winding_normal = element.winding_normal
        theta = winding_normal[1]
        
        # Tính toán vector tác động dựa trên góc xoay hiện tại
        winding_impact = np.array([winding_normal[0] * np.cos(theta), 
                                   winding_normal[0] * np.sin(theta), 
                                   winding_normal[2]])
        
        # Tính mật độ từ thông trung bình đi qua phần tử
        flux_density = element.flux_direct
        b_average = (flux_density[0] + flux_density[1]) * 0.5
        
        # Tính toán đóng góp từ thông $\Phi$ của phần tử
        phi_element = b_average @ winding_impact
        
        # Tích lũy vào tổng từ thông liên kết $\Psi_{total} = \sum (N \cdot \Phi)$
        psi_total += element.element_winding_vector * phi_element

    # 5. ĐỊNH DẠNG ĐẦU RA: [Phase_A, Phase_B, Phase_C, Rotor_Position]
    # Tạo vector cột để lưu kết quả và vị trí góc hiện tại của rotor
    flux_linkage_results = np.empty((phase_number + 1, 1))
    flux_linkage_results[:-1, 0] = psi_total * (machine_factor^0)
    flux_linkage_results[-1] = reluctance_network.mechanical.current_position

    return Output(flux_linkage=flux_linkage_results)