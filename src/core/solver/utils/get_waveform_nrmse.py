import numpy as np
from sklearn.metrics import mean_squared_error
from scipy.interpolate import interp1d

def get_waveform_nrmse(data_true, data_pred, num_points=20, row_index=0):
    """
    Compare two waveforms (possibly with different sampling densities) using NRMSE (%).
    Supports multi-row input; the compared data row is selected by `row_index`.
    If not provided, the first row (0) is used.
    The last row of each input is always considered as the X-axis.
    """
    try:
        y_true_raw = data_true[row_index]
        x_true_raw = data_true[-1]
        y_pred_raw = data_pred[row_index]
        x_pred_raw = data_pred[-1]

        sort_idx_true = np.argsort(x_true_raw)
        x_true, y_true = x_true_raw[sort_idx_true], y_true_raw[sort_idx_true]
        sort_idx_pred = np.argsort(x_pred_raw)
        x_pred, y_pred = x_pred_raw[sort_idx_pred], y_pred_raw[sort_idx_pred]
    except IndexError:
        return np.inf

    start_common = max(np.min(x_true), np.min(x_pred))
    end_common = min(np.max(x_true), np.max(x_pred))
    if start_common >= end_common:
        return np.inf

    x_common = np.linspace(start_common, end_common, num_points)
    kind_true = 'quadratic' if len(x_true) > 2 else 'linear'
    kind_pred = 'quadratic' if len(x_pred) > 2 else 'linear'

    interp_true = interp1d(x_true, y_true, kind=kind_true, bounds_error=False, fill_value=np.nan)
    interp_pred = interp1d(x_pred, y_pred, kind=kind_pred, bounds_error=False, fill_value=np.nan)

    y_true_resampled = interp_true(x_common)
    y_pred_resampled = interp_pred(x_common)

    valid_mask = ~np.isnan(y_true_resampled) & ~np.isnan(y_pred_resampled)
    y_true_common = y_true_resampled[valid_mask]
    y_pred_common = y_pred_resampled[valid_mask]
    if len(y_true_common) < 2:
        return np.inf

    rmse = np.sqrt(mean_squared_error(y_true_common, y_pred_common))
    y_range = np.max(y_true_common) - np.min(y_true_common)
    if y_range == 0:
        return 0.0 if rmse == 0 else np.inf
    return rmse / y_range * 100
