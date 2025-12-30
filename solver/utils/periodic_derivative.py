import numpy as np
from dataclasses import dataclass
from typing import Any
import matplotlib.pyplot as plt

@dataclass
class Output:
    derivative: np.ndarray

def periodic_derivative(data: np.ndarray, half_open_interval: bool = True) -> Output:
    y = data[:-1, :]
    theta = data[-1, :]
    dtheta = theta[1] - theta[0]
    
    if not half_open_interval:
        y_work = y[:, :-1]
    else:
        y_work = y

    y_next = np.roll(y_work, -1, axis=1)
    y_prev = np.roll(y_work, 1, axis=1)
    dy_work = (y_next - y_prev) / (2 * dtheta)

    if not half_open_interval:
        dy = np.hstack((dy_work, dy_work[:, 0:1]))
    else:
        dy = dy_work

    return Output(derivative=np.vstack((dy, theta)))

if __name__ == "__main__":
    # 1. Setup dữ liệu test (Hàm Sine)
    n_points = 50
    theta_half = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    y_half = np.sin(theta_half).reshape(1, -1)
    data_half = np.vstack((y_half, theta_half))

    theta_closed = np.linspace(0, 2*np.pi, n_points + 1, endpoint=True)
    y_closed = np.sin(theta_closed).reshape(1, -1)
    data_closed = np.vstack((y_closed, theta_closed))

    # 2. Tính toán đạo hàm
    res_half = periodic_derivative(data_half, half_open_interval=True)
    res_closed = periodic_derivative(data_closed, half_open_interval=False)

    # 3. Vẽ đồ thị kiểm chứng
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    
    # Đồ thị hàm số và đạo hàm
    ax1.plot(theta_closed, y_closed[0], 'k--', alpha=0.5, label='Original: sin(θ)')
    ax1.plot(res_half.derivative[-1, :], res_half.derivative[0, :], 'ro', mfc='none', label='Numerical (Half-open)')
    ax1.plot(res_closed.derivative[-1, :], res_closed.derivative[0, :], 'b.', label='Numerical (Closed)')
    ax1.plot(theta_closed, np.cos(theta_closed), 'g', alpha=0.6, label='Analytical: cos(θ)')
    ax1.set_ylabel('Amplitude')
    ax1.set_title('Periodic Derivative Verification')
    ax1.legend()
    ax1.grid(True)

    # Đồ thị sai số (Error)
    err_half = res_half.derivative[0, :] - np.cos(theta_half)
    err_closed = res_closed.derivative[0, :] - np.cos(theta_closed)
    
    ax2.plot(theta_half, np.abs(err_half), 'r-', label='Error (Half-open)')
    ax2.plot(theta_closed, np.abs(err_closed), 'b--', label='Error (Closed)')
    ax2.set_xlabel('Theta (rad)')
    ax2.set_ylabel('Absolute Error')
    ax2.set_yscale('log')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()