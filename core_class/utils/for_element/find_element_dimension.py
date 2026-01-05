import numpy as np
from dataclasses import dataclass
from typing import Any

@dataclass
class Output:
    length: Any          # Mảng 2x3: [lr, lt, lz] cho 2 nửa
    length_ratio: Any    # Tỷ lệ chiều dài
    section_area: Any    # Mảng 2x3: [Sr, St, Sz] cho 2 nửa

def find_element_dimension(coordinate):
    """
    Tính toán kích thước phần tử từ trở dựa trên tọa độ đầu vào.
    
    Args:
        coordinate (np.ndarray): Ma trận 2x3 chứa:
            [[r_in,  theta_1, z_bottom],
             [r_out, theta_2, z_top]]
             
    Returns:
        Output: Object chứa length, length_ratio, section_area đúng chuẩn PDF.
    """
    
    # 1. Trích xuất dữ liệu đầu vào
    r_in  = coordinate[0, 0]
    r_out = coordinate[1, 0]
    
    theta_1 = coordinate[0, 1]
    theta_2 = coordinate[1, 1]
    
    z_bottom = coordinate[0, 2]
    z_top    = coordinate[1, 2]

    # 2. Tính các thông số cơ bản
    # Góc mở (theta) và một nửa góc mở (theta/2)
    open_angle = np.abs(theta_1 - theta_2)
    half_open  = open_angle / 2
    
    # Chiều cao dọc trục tổng (lz)
    total_lz = np.abs(z_top - z_bottom)
    
    # Chiều cao phần tử hướng tâm (l7 trong hình vẽ)
    radial_height = (r_out - r_in) * np.cos(half_open)

    # 3. Khởi tạo mảng kết quả
    # Cấu trúc: Hàng 0 = Nửa dưới/trong (index 0), Hàng 1 = Nửa trên/ngoài (index 1)
    # Cột: 0 = Hướng tâm (r), 1 = Tiếp tuyến (t), 2 = Dọc trục (z)
    length = np.zeros((2, 3))
    section_area = np.zeros((2, 3))

    # ==========================================
    # 4. TÍNH TOÁN CHIỀU DÀI (LENGTH - l)
    # ==========================================
    
    # [Cột 0] Hướng tâm (lr): l_r0 = l_r1 = (rout - rin)/2 * cos(theta/2)
    # Nguồn: Slide 3 
    l_r_val = ((r_out - r_in) / 2) * np.cos(half_open)
    length[:, 0] = l_r_val

    # [Cột 1] Tiếp tuyến (lt): l_t = Bề rộng trung bình
    # Công thức: (rin + rout)/2 * sin(theta/2)
    # Nguồn: Slide 4 (suy ra từ công thức l_t0) [cite: 34]
    l_t_val = ((r_in + r_out) / 2) * np.sin(half_open)
    length[:, 1] = l_t_val

    # [Cột 2] Dọc trục (lz): l_z0 = l_z1 = lz / 2
    # Nguồn: Slide 5 [cite: 46]
    l_z_val = total_lz / 2
    length[:, 2] = l_z_val

    # ==========================================
    # 5. TÍNH TOÁN DIỆN TÍCH (SECTION AREA - S)
    # ==========================================

    # [Cột 0] Hướng tâm (Sr): Diện tích mặt cong
    # Nguồn: Slide 3 [cite: 11, 20]
    # Sr_0 (Bottom/Inner side): Dùng công thức (3/2 rin + 1/2 rout)
    section_area[0, 0] = total_lz * (1.5 * r_in + 0.5 * r_out) * np.sin(half_open)
    # Sr_1 (Top/Outer side): Dùng công thức (3/2 rout + 1/2 rin)
    section_area[1, 0] = total_lz * (1.5 * r_out + 0.5 * r_in) * np.sin(half_open)

    # [Cột 1] Tiếp tuyến (St): Diện tích mặt cắt dọc (SỬA LẠI TỪ BẢN CŨ CỦA BẠN)
    # Công thức đúng: S = lz * l7 = lz * (rout - rin) * cos(theta/2)
    # Nguồn: Slide 4 
    s_t_val = total_lz * radial_height
    section_area[:, 1] = s_t_val

    # [Cột 2] Dọc trục (Sz): Diện tích hình thang đáy
    # Công thức: (rout^2 - rin^2) * sin(theta/2) * cos(theta/2)
    # Nguồn: Slide 5 [cite: 47]
    s_z_val = (r_out**2 - r_in**2) * np.sin(half_open) * np.cos(half_open)
    section_area[:, 2] = s_z_val

    # 6. Tính tỷ lệ chiều dài (Length Ratio)
    # Thường sẽ là [1, 1, 1] vì phần tử đối xứng qua tâm, nhưng giữ lại theo yêu cầu
    # Tránh chia cho 0 bằng cách cộng epsilon hoặc kiểm tra
    length_ratio = np.divide(length[0, :], length[1, :], out=np.ones(3), where=length[1, :]!=0)

    return Output(length=length,
                  length_ratio=length_ratio,
                  section_area=section_area)