import paths
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.interpolate import interp1d
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse

def synchronize_signals(data_true, data_pred, is_periodic=True, half_open_interval=True):
    # Sao chep truc toa do de lam tham chieu co dinh
    x_fixed = data_pred[-1].copy()
    n_rows, n_points = data_pred.shape
    x_min, x_max = np.min(x_fixed), np.max(x_fixed)
    
    if half_open_interval and n_points > 1:
        dx = (x_max - x_min) / (n_points - 1)
        period = (x_max - x_min) + dx
    else:
        period = x_max - x_min

    def objective(shift):
        temp_pred = data_pred.copy()
        if is_periodic and period > 0:
            new_x = (x_fixed + shift - x_min) % period + x_min
            sort_idx = np.argsort(new_x)
            temp_pred = temp_pred[:, sort_idx]
            temp_pred[-1] = new_x[sort_idx]
            _, unique_indices = np.unique(temp_pred[-1], return_index=True)
            temp_pred = temp_pred[:, unique_indices]
        else:
            temp_pred[-1] = x_fixed + shift
            
        return get_waveform_nrmse(data_true, temp_pred, num_points=100, row_index=2)

    search_bound = period / 2 if is_periodic else np.pi
    res = minimize_scalar(objective, bounds=(-search_bound, search_bound), method='bounded')
    optimal_shift = res.x

    # Sua truc tiep tren data_pred
    for i in range(n_rows - 1):
        y_orig = data_pred[i].copy() 
        
        if is_periodic and period > 0:
            x_ext = np.concatenate([x_fixed - period, x_fixed, x_fixed + period])
            y_ext = np.concatenate([y_orig, y_orig, y_orig])
            idx_ext = np.argsort(x_ext)
            f_interp = interp1d(x_ext[idx_ext], y_ext[idx_ext], kind='quadratic', fill_value="extrapolate")
            
            # Ghi de truc tiep vao hang i cua mảng gốc
            data_pred[i, :] = f_interp(x_fixed - optimal_shift)
        else:
            f_interp = interp1d(x_fixed, y_orig, kind='quadratic', fill_value="extrapolate", bounds_error=False)
            data_pred[i, :] = f_interp(x_fixed - optimal_shift)

    # Hang cuoi data_pred[-1] khong thay doi do da co dinh tu dau
    return optimal_shift