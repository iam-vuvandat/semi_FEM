from dataclasses import dataclass
import numpy as np
from material.core.lookup_BH_curve import lookup_BH_curve

@dataclass
class Output:
    relative_permeability: np.ndarray
    d_relative_permeability_d_B: np.ndarray

def find_relative_permeability(element, 
                               material_relaxation_factor=1.0,
                               delta_mu_max=-1):
    # Khởi tạo giá trị mặc định (shape 2x3 cho phần tử hình thang cân)
    relative_permeability = np.ones((2, 3))
    d_relative_permeability_d_B = np.zeros((2, 3))

    # Lấy giá trị từ bước trước trong bộ nhớ phần tử
    current_mu = element.relative_permeability if element.relative_permeability is not None else np.ones((2, 3))
    current_dmu = element.d_relative_permeability_d_B if element.d_relative_permeability_d_B is not None else np.zeros((2, 3))

    if element.material == "iron":
        # 1. Tra cứu đường cong B-H
        data = lookup_BH_curve(B_input=element.flux_density_direct, 
                               material_database=element.material_database, 
                               return_du_dB=True)
        
        next_mu_raw = data.mu_r if data.mu_r is not None else 1.0
        next_dmu_raw = data.dmu_r_dB if data.dmu_r_dB is not None else 0.0

        # 2. Tính toán mu đề xuất có áp dụng damping
        mu_proposed = (1 - material_relaxation_factor) * current_mu + \
                      material_relaxation_factor * next_mu_raw
        
        # 3. Logic điều khiển giới hạn cập nhật
        if delta_mu_max == -1: 
            # Không giới hạn: lấy trực tiếp giá trị đề xuất
            relative_permeability = mu_proposed
        else:
            # Có giới hạn: ép bước nhảy không vượt quá delta_mu_max
            relative_permeability = np.clip(mu_proposed, 
                                            a_min=current_mu - delta_mu_max, 
                                            a_max=current_mu + delta_mu_max)
        
        # Đảm bảo mu không nhỏ hơn 1 (không khí) và cập nhật đạo hàm
        relative_permeability = np.maximum(relative_permeability, 1.0)
        d_relative_permeability_d_B = (1 - material_relaxation_factor) * current_dmu + \
                                      material_relaxation_factor * next_dmu_raw

    elif element.material == "magnet":
        mu_m = element.material_database.magnet.relative_permeance
        relative_permeability = np.ones((2, 3)) * mu_m
        d_relative_permeability_d_B = np.zeros((2, 3))

    else:
        mu_g = element.material_database.air.relative_permeance
        relative_permeability = np.ones((2, 3)) * mu_g
        d_relative_permeability_d_B = np.zeros((2, 3))

    return Output(relative_permeability=relative_permeability,
                  d_relative_permeability_d_B=d_relative_permeability_d_B)