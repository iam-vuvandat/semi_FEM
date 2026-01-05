from dataclasses import dataclass
from typing import Any
import numpy as np

@dataclass
class Output:
    magnet_source : Any


def find_magnet_source(element):
    """
        Đối với các mảng (2x3) chứa nhiều thông tin, vị trí tương ứng:
        [     r_in    t_left     z_bot
              r_out   t_right    z_top    ]
    """
    
    # Độ lớn vector từ hóa của segment:
    absFseg = element.segment_magnet_source

    # Vector chỉ phương (độ lớn vector chỉ phương := 1)
    u = element.magnetization_direction

    # Vector từ hóa của segment (xử lý trong hệ tọa độ trụ):
    Fseg = np.zeros(3)
    Fseg[2] = absFseg * u[2]
    Fseg[1] = absFseg * u[0] * np.sin(u[1])
    Fseg[0] = absFseg * u[0] * np.cos(u[1])

    

    # Tỉ lệ kích thước của element (con) và segment (mẹ)
    dimension_ratio = element.dimension_ratio

    # Vector từ hóa Element:
    Fele = Fseg * dimension_ratio

    # Vector từ hóa của từng nhánh
    F_direc = Fele/2
    F_direct = np.vstack((F_direc,F_direc))

    return Output(magnet_source = F_direct)