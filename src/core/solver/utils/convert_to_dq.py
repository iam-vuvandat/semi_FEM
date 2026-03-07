import numpy as np

def convert_to_dq(value, poles, current_position):
    n_phase = value.shape[0] - 1
    p = poles / 2
    theta_e = current_position * p
    alpha = (2 * np.pi) / n_phase
    
    psi_d = np.zeros_like(theta_e)
    psi_q = np.zeros_like(theta_e)
    
    for k in range(n_phase):
        angle_shift = k * alpha
        # Thay doi += bang phep gan truc tiep de tu dong broadcast shape
        psi_d = psi_d + value[k, :] * np.cos(theta_e - angle_shift)
        psi_q = psi_q - value[k, :] * np.sin(theta_e - angle_shift)
        
    psi_d = (2 / n_phase) * psi_d
    psi_q = (2 / n_phase) * psi_q
    
    return np.vstack((psi_d, psi_q, current_position))