import numpy as np
from dataclasses import dataclass

@dataclass
class Output:
    duplicated_data: np.ndarray

def duplicate_data(data: np.ndarray, half_open_interval: bool = True) -> Output:
    """
    Nhân đôi chuỗi dữ liệu tuần hoàn.
    Hàng cuối cùng của 'data' được hiểu là tọa độ góc (theta).
    """
    # 1. Tách dữ liệu vật lý (y) và tọa độ góc (theta)
    y = data[:-1, :]
    theta = data[-1, :]
    
    # Tính bước nhảy dtheta và chu kỳ T
    dtheta = theta[1] - theta[0]
    
    if half_open_interval:
        # TRƯỜNG HỢP KHOẢNG NỬA MỞ [0, 2pi)
        # Tọa độ theta tiếp theo bắt đầu ngay sau điểm cuối cùng
        period = theta[-1] + dtheta - theta[0]
        
        y_double = np.hstack((y, y))
        theta_double = np.hstack((theta, theta + period))
    else:
        # TRƯỜNG HỢP KHOẢNG ĐÓNG [0, 2pi] (Điểm đầu và cuối trùng giá trị vật lý)
        # Ta cần loại bỏ điểm cuối của đoạn 1 để tránh lặp dữ liệu tại điểm nối
        period = theta[-1] - theta[0]
        
        y_double = np.hstack((y[:, :-1], y))
        theta_double = np.hstack((theta[:-1], theta + period))

    # 2. Ghép lại thành mảng (y_double nằm trên, theta_double nằm dưới)
    res = np.vstack((y_double, theta_double))
    
    return Output(duplicated_data=res)