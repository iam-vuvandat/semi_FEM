import numpy as np
from dataclasses import dataclass

@dataclass
class Output:
    duplicated_data: np.ndarray

def duplicate_data(data: np.ndarray, half_open_interval: bool = True, num_periods: int = 2) -> Output:
    """
    Nhân đôi chuỗi dữ liệu tuần hoàn.
    Hàng cuối cùng của 'data' được hiểu là tọa độ góc (theta).
    """
    if num_periods < 1:
        return Output(duplicated_data=data)

    y = data[:-1, :]
    theta = data[-1, :]
    
    dtheta = theta[1] - theta[0]
    
    if half_open_interval:
        period = theta[-1] + dtheta - theta[0]
        
        y_list = [y] * num_periods
        y_double = np.hstack(y_list)
        
        theta_list = [theta + i * period for i in range(num_periods)]
        theta_double = np.hstack(theta_list)
    else:
        period = theta[-1] - theta[0]
        
        y_list = [y[:, :-1]] * (num_periods - 1) + [y]
        y_double = np.hstack(y_list)
        
        theta_list = [theta[:-1] + i * period for i in range(num_periods - 1)] + [theta + (num_periods - 1) * period]
        theta_double = np.hstack(theta_list)

    res = np.vstack((y_double, theta_double))
    
    return Output(duplicated_data=res)