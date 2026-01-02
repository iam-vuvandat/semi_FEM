import numpy as np
from dataclasses import dataclass
from typing import Any

@dataclass
class Output:
    length: Any         # Mảng 2x3: [lr, lt, lz] cho 2 nửa
    length_ratio: Any    # Tỷ lệ chiều dài
    section_area: Any    # Mảng 2x3: [Sr, St, Sz] cho 2 nửa

def find_element_dimension(coordinate):
    """
    Tính toán kích thước phần tử: Giữ nguyên công thức gốc, 
    trung bình cộng kết quả ở bước cuối để đảm bảo đối xứng ma trận.
    """
    
    # 1. Trích xuất dữ liệu đầu vào
    r_in  = coordinate[0, 0]
    r_out = coordinate[1, 0]
    theta_1 = coordinate[0, 1]
    theta_2 = coordinate[1, 1]
    z_bottom = coordinate[0, 2]
    z_top    = coordinate[1, 2]

    # 2. Các thông số trung gian
    open_angle = np.abs(theta_1 - theta_2)
    half_open  = open_angle / 2
    total_lz   = np.abs(z_top - z_bottom)
    radial_height = (r_out - r_in) * np.cos(half_open)

    # Khởi tạo mảng kết quả
    length = np.zeros((2, 3))
    section_area = np.zeros((2, 3))

    # ==========================================
    # 3. TÍNH CHIỀU DÀI (GIỮ NGUYÊN CÔNG THỨC GỐC)
    # ==========================================
    l_r_val = ((r_out - r_in) / 2) * np.cos(half_open)
    l_t_val = ((r_in + r_out) / 2) * np.sin(half_open)
    l_z_val = total_lz / 2

    length[0, :] = [l_r_val, l_t_val, l_z_val] # Nửa trong/dưới
    length[1, :] = [l_r_val, l_t_val, l_z_val] # Nửa ngoài/trên

    # ==========================================
    # 4. TÍNH DIỆN TÍCH (GIỮ NGUYÊN CÔNG THỨC GỐC)
    # ==========================================
    
    # [Hướng tâm Sr] - Tính riêng biệt theo 2 công thức gốc của bạn
    sr_0 = total_lz * (1.5 * r_in + 0.5 * r_out) * np.sin(half_open)
    sr_1 = total_lz * (1.5 * r_out + 0.5 * r_in) * np.sin(half_open)
    
    # [Tiếp tuyến St]
    st_val = total_lz * radial_height
    
    # [Dọc trục Sz]
    sz_val = (r_out**2 - r_in**2) * np.sin(half_open) * np.cos(half_open)

    # Gán giá trị tính toán được vào mảng
    section_area[0, 0] = sr_0  # Inner Sr
    section_area[1, 0] = sr_1  # Outer Sr
    section_area[:, 1] = st_val
    section_area[:, 2] = sz_val

    # ==========================================
    # 5. BƯỚC TRUNG BÌNH CỘNG (CẢI TIẾN ĐỐI XỨNG)
    # Thực hiện sau khi đã có đầy đủ giá trị từ công thức gốc
    # ==========================================
    
    # Trung bình cộng diện tích Sr (Vì Sr_0 != Sr_1 trong tọa độ cực)
    sr_avg = (section_area[0, 0] + section_area[1, 0]) / 2
    section_area[0, 0] = sr_avg
    section_area[1, 0] = sr_avg
    
    # Trung bình cộng chiều dài (Nếu sau này bạn có công thức lr_0 khác lr_1)
    l_avg = (length[0, :] + length[1, :]) / 2
    length[0, :] = l_avg
    length[1, :] = l_avg

    # 6. Tính tỷ lệ chiều dài (Sẽ ra [1, 1, 1])
    length_ratio = np.ones(3)

    return Output(length=length,
                  length_ratio=length_ratio,
                  section_area=section_area)