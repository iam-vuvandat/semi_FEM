import numpy as np

def _compute_component_metrics(arr_mbgrn, arr_fem):
    comp_metrics = {
        "mbgrn_max": "N/A", "mbgrn_rms": "N/A", "mbgrn_mean": "N/A", "mbgrn_amp": "N/A", "mbgrn_ripple": "N/A",
        "fem_max": "N/A", "fem_rms": "N/A", "fem_mean": "N/A", "fem_amp": "N/A", "fem_ripple": "N/A",
        "error_max": "N/A", "error_rms": "N/A", "error_mean": "N/A", "error_ripple": "N/A"
    }
    
    if arr_mbgrn is not None and len(arr_mbgrn) > 0:
        v_max = float(np.max(arr_mbgrn))
        v_min = float(np.min(arr_mbgrn))
        v_mean = float(np.mean(arr_mbgrn))
        v_rms = float(np.sqrt(np.mean(np.square(arr_mbgrn))))
        v_amp = (v_max - v_min) / 2.0
        v_ripple = ((v_max - v_min) / np.abs(v_mean) * 100) if v_mean != 0 else 0.0
        
        comp_metrics["mbgrn_max"] = f"{v_max:.2f}"
        comp_metrics["mbgrn_rms"] = f"{v_rms:.2f}"
        comp_metrics["mbgrn_mean"] = f"{v_mean:.2f}"
        comp_metrics["mbgrn_amp"] = f"{v_amp:.2f}"
        comp_metrics["mbgrn_ripple"] = f"{v_ripple:.2f}%"

    if arr_fem is not None and len(arr_fem) > 0:
        f_max = float(np.max(arr_fem))
        f_min = float(np.min(arr_fem))
        f_mean = float(np.mean(arr_fem))
        f_rms = float(np.sqrt(np.mean(np.square(arr_fem))))
        f_amp = (f_max - f_min) / 2.0
        f_ripple = ((f_max - f_min) / np.abs(f_mean) * 100) if f_mean != 0 else 0.0
        
        comp_metrics["fem_max"] = f"{f_max:.2f}"
        comp_metrics["fem_rms"] = f"{f_rms:.2f}"
        comp_metrics["fem_mean"] = f"{f_mean:.2f}"
        comp_metrics["fem_amp"] = f"{f_amp:.2f}"
        comp_metrics["fem_ripple"] = f"{f_ripple:.2f}%"

        if arr_mbgrn is not None and len(arr_mbgrn) > 0:
            err_max = (np.abs(np.abs(v_max) - np.abs(f_max)) / np.abs(f_max) * 100) if f_max != 0 else 0.0
            err_rms = (np.abs(v_rms - f_rms) / f_rms * 100) if f_rms != 0 else 0.0
            err_mean = (np.abs(np.abs(v_mean) - np.abs(f_mean)) / np.abs(f_mean) * 100) if f_mean != 0 else 0.0
            err_ripple = (np.abs(v_ripple - f_ripple) / f_ripple * 100) if f_ripple != 0 else 0.0
            
            comp_metrics["error_max"] = f"{err_max:.2f}%"
            comp_metrics["error_rms"] = f"{err_rms:.2f}%"
            comp_metrics["error_mean"] = f"{err_mean:.2f}%"
            comp_metrics["error_ripple"] = f"{err_ripple:.2f}%"
            
    return comp_metrics

def update_torque_data(data_processor, revert=False):
    motor = data_processor.motor
    record = motor.record

    t_mbgrn = record.torque if hasattr(record, "torque") else None
    t_fem = record.torque_fem if hasattr(record, "torque_fem") else None
    fem_mult = -1 if revert else 1

    val_mbgrn = t_mbgrn[0, :] if t_mbgrn is not None else None
    val_fem = (t_fem[0, :] * fem_mult) if t_fem is not None else None

    record.torque_metrics = _compute_component_metrics(val_mbgrn, val_fem)
    return True