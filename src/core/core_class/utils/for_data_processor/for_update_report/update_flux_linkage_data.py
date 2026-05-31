import numpy as np
from src.core.solver.utils.decompose_harmonics import decompose_harmonics

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

def update_flux_linkage_data(data_processor):
    motor = data_processor.motor
    record = motor.record
    max_h = 15

    psi_mbgrn = record.flux_linkage if hasattr(record, "flux_linkage") else None
    psi_fem = record.flux_linkage_fem if hasattr(record, "flux_linkage_fem") else None

    psia_mbgrn = psi_mbgrn[2, :] if psi_mbgrn is not None else None
    psia_fem = psi_fem[2, :] if psi_fem is not None else None

    record.flux_linkage_metrics = _compute_component_metrics(psia_mbgrn, psia_fem)

    if psia_mbgrn is not None:
        amps_mrn, _ = decompose_harmonics(psia_mbgrn, n_harmonics=max_h)
        h_orders = np.arange(len(amps_mrn))
        record.flux_linkage_harmonic = np.vstack((amps_mrn, h_orders))

    if psia_fem is not None:
        amps_fem, _ = decompose_harmonics(psia_fem, n_harmonics=max_h)
        h_orders = np.arange(len(amps_fem))
        record.flux_linkage_harmonic_fem = np.vstack((amps_fem, h_orders))

    return True