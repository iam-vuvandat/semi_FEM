import numpy as np

def periodic_derivative(data):
    """
    Đạo hàm dữ liệu tuần hoàn theo biến theta.
    data: ndarray có dạng (n_y + 1, n_x)
          - các hàng đầu là dữ liệu (y)
          - hàng cuối là góc rotor (theta)
    Giả định: data đã có điểm đầu và cuối trùng nhau.
    """
    y = data[:-1, :]
    theta = data[-1, :]

    n = len(theta)
    dtheta = theta[1] - theta[0]  # giả định lưới đều

    dydtheta = np.zeros_like(y)

    for i in range(n):
        if i == 0:
            # điểm đầu: lấy phần tử gần cuối (trừ 2) vì cuối cùng trùng đầu
            i_prev = n - 2
            i_next = i + 1
        elif i == n - 1:
            # điểm cuối: trùng với đầu → dùng đạo hàm giống điểm đầu
            dydtheta[:, i] = dydtheta[:, 0]
            continue
        else:
            i_prev = i - 1
            i_next = i + 1

        dydtheta[:, i] = (y[:, i_next] - y[:, i_prev]) / (2 * dtheta)

    # Ghép lại với theta
    return np.vstack((dydtheta, theta))
