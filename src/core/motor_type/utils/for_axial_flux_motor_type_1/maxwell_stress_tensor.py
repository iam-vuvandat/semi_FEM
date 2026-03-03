from typing import Any
from src.core.core_class.models.MaxwellIntegrationSurface import MaxwellIntegrationSurface
from dataclasses import dataclass
import numpy as np 

@dataclass
class Output:
    mst_result: Any

def maxwell_stress_tensor(motor):
    # lấy thông tin của lưới thích nghi: 
    adaptive_mesh_data = motor.mesh.adaptive_mesh_data
    n_z_in_air      = adaptive_mesh_data.n_z_in_air
    n_z_rotor_yoke  = adaptive_mesh_data.n_z_rotor_yoke
    n_z_magnet      = adaptive_mesh_data.n_z_magnet
    n_z_airgap      = adaptive_mesh_data.n_z_airgap

    z_air_cell_index = int(n_z_in_air + n_z_rotor_yoke + n_z_magnet + (n_z_airgap // 2) -1 )

    # Trích xuất đến mảng elements global:
    elements = motor.reluctance_network.elements
    # Tạo 4 mặt phẳng bao quanh rotor: 
    # 1. mặt phẳng ở bên dưới rotor: 
    surface1 = MaxwellIntegrationSurface(elements= elements,
                                         plane = "Ort",
                                         direction= -1)
    
    surface1.create_plane(layer= 0)
    result1 =  surface1.integrate_maxwell_stress_tensor()
    
    #2. mặt phẳng bên trên rotor: 
    surface2 = MaxwellIntegrationSurface(elements= elements,
                                         plane = "Ort",
                                         direction= 1)
    surface2.create_plane(layer= z_air_cell_index)
    result2 = surface2.integrate_maxwell_stress_tensor()
    
    # 3. Mặt phẳng bán kính trong: 
    surface3 = MaxwellIntegrationSurface(elements= elements,
                                         plane = "Otz",
                                         direction= -1)
    
    surface3.create_plane(layer = 0 , b2 = z_air_cell_index)
    result3 = surface3.integrate_maxwell_stress_tensor()

    # 4. Mặt phẳng bán kính ngoài 
    surface4 = MaxwellIntegrationSurface(elements= elements,
                                         plane = "Otz",
                                         direction= 1)

    surface4.create_plane(b2 = z_air_cell_index)
    result4 = surface4.integrate_maxwell_stress_tensor()
    
    # 5. Khởi tạo mảng maxwell stress tensor: 
    mst_result = np.zeros(5)
    
    # 6. Tham chiếu đến vị trí hiện tại
    mst_result[-1] = motor.reluctance_network.mechanical.current_position
    
    # 7. Cộng các giá trị vừa tích phân xong: 
    result = result1 + result2 + result3 + result4
    

    # 8. Xử lý symmetry factor
    # kiểm tra xem có dùng hệ số đối xứng không: 
    #use_symmetry_factor = adaptive_mesh_data.use_symmetry_factor
    #if use_symmetry_factor:
    #    result = result * motor.mechanical.symmetry_factor

    # 8. Gán vào mảng kết quả 
    mst_result[0] = result[0]
    mst_result[1] = result[1]
    mst_result[2] = result[2]
    mst_result[3] = result[3]


    return Output(mst_result= mst_result)