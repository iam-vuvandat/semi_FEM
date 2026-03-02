import numpy as np
from scipy.sparse.linalg import norm, onenormest, splu, LinearOperator

def solve(reluctance_network, 
         max_iteration=50,
         max_relative_residual=0.05, 
         material_relax=0.2, 
         damping_factor=0.5,   
         debug=True):
    
    factor_1 = 0.5

    G_c, Y_c, R_c, B_c, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[94m", "\033[0m"

    best_residual_history = []
    reluctance_network.set_reluctance_at_zero()
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    
    x_k = reluctance_network.magnetic_potential.data.flatten(order='F')[:-1]
    best_pot_data = reluctance_network.magnetic_potential.data.copy()
    best_phi = float('inf') 
    
    current_relax = material_relax

    def compute_system(x_vec, relax):
        reluctance_network.magnetic_potential.data = np.append(x_vec, 0.0).reshape(mag_pot_shape, order='F')
        reluctance_network.update_reluctance_network(
            magnetic_potential=reluctance_network.magnetic_potential,
            update_for_magnetic_potential = True,
            material_relaxation_factor=relax, 
            delta_mu_max=-1 
        )
        comp = reluctance_network.create_magnetic_potential_equation(load_factor=1.0)
        F_x = comp.G.dot(x_vec) - comp.J
        return F_x, comp.G, comp.J

    F_k, G_k, J_k = compute_system(x_k, current_relax)
    B_k = G_k.tocsc() 

    for j in range(1, max_iteration + 1):
        try:
            lu_obj = splu(B_k)
            delta_x = -lu_obj.solve(F_k)
        except Exception as e:
            if debug: print(f"{R_c}Solver Error: {e}{RESET}")
            break

        x_next = x_k + damping_factor * delta_x
        
        F_next, G_next, J_next = compute_system(x_next, current_relax)
        phi_true = np.linalg.norm(F_next) / (np.linalg.norm(J_next) + 1e-12)

        if debug:
            color = G_c if phi_true <= max_relative_residual else (R_c if phi_true >= best_phi else RESET)
            print(f"{color}Iteration {j}: relative residual = {phi_true*100:.2f}%, Relax = {current_relax:.4f}{RESET}")

        if phi_true <= max_relative_residual:
            best_phi = phi_true
            best_pot_data = reluctance_network.magnetic_potential.data.copy()
            break
        
        if phi_true < best_phi:
            best_phi = phi_true
            best_pot_data = reluctance_network.magnetic_potential.data.copy()
        elif phi_true > best_phi * 2.0:
            break

        # Giam material_damping (current_relax) theo factor_1
        current_relax *= factor_1
        F_next, G_next, J_next = compute_system(x_next, current_relax)

        B_k = G_next.tocsc() 
        x_k = x_next
        F_k = F_next
        best_residual_history.append(phi_true)

    reluctance_network.magnetic_potential.data = best_pot_data
    return best_phi, best_residual_history