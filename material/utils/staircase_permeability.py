import numpy as np

def staircase_permeability(iron, num_steps=8):
    iron.backup_B_H_curve = {
        "B_data": iron.B_H_curve["B_data"].copy(),
        "H_data": iron.B_H_curve["H_data"].copy()
    }
    
    B = iron.B_H_curve["B_data"]
    H = iron.B_H_curve["H_data"]
    
    mu_real = np.zeros_like(B)
    mu_real[1:] = B[1:] / H[1:]
    mu_real[0] = mu_real[1] 
    
    mu_min, mu_max = np.min(mu_real), np.max(mu_real)
    # Thay đổi từ np.geomspace sang np.linspace để các bậc thang đều nhau
    levels = np.linspace(mu_min, mu_max, num_steps)
    
    mu_staircase = np.array([levels[np.abs(levels - m).argmin()] for m in mu_real])
    
    H_staircase = np.zeros_like(H)
    mask = mu_staircase > 0
    H_staircase[mask] = B[mask] / mu_staircase[mask]
    H_staircase[~mask] = 0.0
    
    iron.B_H_curve["H_data"] = H_staircase

    return iron