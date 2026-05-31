import numpy as np

def _compute_component_metrics(arr_mbgrn, arr_fem):
    comp_metrics = {
        "mbgrn_max": "N/A", "mbgrn_rms": "N/A", "mbgrn_mean": "N/A", "mbgrn_amp": "N/A",
        "fem_max": "N/A", "fem_rms": "N/A", "fem_mean": "N/A", "fem_amp": "N/A",
        "error_max": "N/A", "error_rms": "N/A", "error_mean": "N/A"
    }
    
    if arr_mbgrn is not None and len(arr_mbgrn) > 0:
        v_max = float(np.max(arr_mbgrn))
        v_min = float(np.min(arr_mbgrn))
        v_mean = float(np.mean(arr_mbgrn))
        v_rms = float(np.sqrt(np.mean(np.square(arr_mbgrn))))
        v_amp = (v_max - v_min) / 2.0
        
        comp_metrics["mbgrn_max"] = f"{v_max:.2f}"
        comp_metrics["mbgrn_rms"] = f"{v_rms:.2f}"
        comp_metrics["mbgrn_mean"] = f"{v_mean:.2f}"
        comp_metrics["mbgrn_amp"] = f"{v_amp:.2f}"

    if arr_fem is not None and len(arr_fem) > 0:
        f_max = float(np.max(arr_fem))
        f_min = float(np.min(arr_fem))
        f_mean = float(np.mean(arr_fem))
        f_rms = float(np.sqrt(np.mean(np.square(arr_fem))))
        f_amp = (f_max - f_min) / 2.0
        
        comp_metrics["fem_max"] = f"{f_max:.2f}"
        comp_metrics["fem_rms"] = f"{f_rms:.2f}"
        comp_metrics["fem_mean"] = f"{f_mean:.2f}"
        comp_metrics["fem_amp"] = f"{f_amp:.2f}"

        if arr_mbgrn is not None and len(arr_mbgrn) > 0:
            err_max = (abs(v_max - f_max) / f_max * 100) if f_max != 0 else 0.0
            err_rms = (abs(v_rms - f_rms) / f_rms * 100) if f_rms != 0 else 0.0
            err_mean = (abs(v_mean - f_mean) / f_mean * 100) if f_mean != 0 else 0.0
            
            comp_metrics["error_max"] = f"{err_max:.2f}%"
            comp_metrics["error_rms"] = f"{err_rms:.2f}%"
            comp_metrics["error_mean"] = f"{err_mean:.2f}%"
            
    return comp_metrics

def update_back_emf_no_load_data(data_processor):
    motor = data_processor.motor
    record = motor.record

    e_mbgrn = record.back_emf_no_load if hasattr(record, "back_emf_no_load") else None
    e_fem = record.back_emf_no_load_fem if hasattr(record, "back_emf_no_load_fem") else None

    ea_mbgrn = e_mbgrn[0, :] if e_mbgrn is not None else None
    ea_fem = e_fem[0, :] if e_fem is not None else None

    record.back_emf_no_load_metrics = _compute_component_metrics(ea_mbgrn, ea_fem)
    return True