import paths
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse

def synchronize_signals(data_true, data_pred):
    # Kiem tra va loai bo diem cuoi neu trung voi diem dau (tinh tuan hoan)
    if np.allclose(data_pred[:, 0], data_pred[:, -1]):
        data_pred = data_pred[:, :-1]
        
    def objective(shift):
        temp_pred = data_pred.copy()
        temp_pred[-1] = data_pred[-1] + shift
        return get_waveform_nrmse(data_true, temp_pred, num_points=100, row_index=2)

    res = minimize_scalar(objective, bounds=(-np.pi, np.pi), method='bounded')
    optimal_shift = res.x

    data_synchronized = data_pred.copy()
    data_synchronized[-1] = data_pred[-1] + optimal_shift

    return optimal_shift, data_synchronized

if __name__ == "__main__":
    # 1. Gia lap du lieu co diem cuoi trung diem dau (0 den 2*pi inclusive)
    theta = np.linspace(0, 2 * np.pi, 101) # 101 diem de diem cuoi la 2*pi
    
    psi_true = 0.05 * np.sin(theta)
    # Tin hieu du doan bi lech pha va co diem cuoi trung diem dau
    psi_pred = 0.048 * np.sin(theta - 0.5)

    d_true = np.zeros((4, 101))
    d_true[2] = psi_true
    d_true[-1] = theta

    d_pred = np.zeros((4, 101))
    d_pred[2] = psi_pred
    d_pred[-1] = theta

    # 2. Thuc hien dong bo hoa (Ham se tu loai bo diem thu 101 cua d_pred)
    shift_val, d_sync = synchronize_signals(d_true, d_pred)

    # 3. Tinh toan sai so
    nrmse_before = get_waveform_nrmse(d_true, d_pred, row_index=2)
    nrmse_after = get_waveform_nrmse(d_true, d_sync, row_index=2)

    print(f"Ket qua dieu chinh lech pha:")
    print(f"- So luong diem ban dau: {d_pred.shape[1]}")
    print(f"- So luong diem sau khi loc: {d_sync.shape[1]}")
    print(f"- Goc lech tim duoc: {shift_val:.6f} rad")
    print(f"- NRMSE sau khi dong bo: {nrmse_after:.4f} %")

    # 4. Ve do thi
    plt.figure(figsize=(10, 6))
    plt.plot(d_true[-1], d_true[2], 'k-', label='True Signal (FEM)', linewidth=2)
    plt.plot(d_pred[-1], d_pred[2], 'r--', label='Original Pred (Redundant)', alpha=0.5)
    plt.plot(d_sync[-1], d_sync[2], 'g:', label='Synchronized & Cleaned', linewidth=2.5)
    
    plt.title("Synchronize Signals with Redundant Point Removal", fontweight='bold')
    plt.xlabel("Theta (rad)")
    plt.ylabel("Flux (Wb)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()