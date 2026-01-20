import numpy as np
from scipy.sparse.linalg import spsolve, norm, onenormest, splu, LinearOperator

def adaptive_broyden_iteration_for_magnetic_potential(reluctance_network, 
                                                       max_iteration=50,
                                                       max_relative_residual=0.05, 
                                                       material_relax=0.2, 
                                                       damping_factor=0.5,   
                                                       debug=True):
    
    ADAPTIVE_FACTOR_1 = 0.2
    ADAPTIVE_FACTOR_2 = 0.5

    G_c, Y_c, R_c, C_c, B_c, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[96m", "\033[94m", "\033[0m"

    if debug: 
        print(f"\n{Y_c}{'='*120}")
        print(f" ADAPTIVE BROYDEN QUASI-NEWTON (L-Triggered Relaxation)")
        print(f" Relax: {material_relax} | Damping: {damping_factor} | Target Res: {max_relative_residual*100}%")
        print(f"{'='*120}{RESET}")
        print(f"{B_c}{'Iter':>4} | {'F(x) Norm':>12} | {'Curr Res':>12} | {'Best Res':>12} | {'Step Norm':>10} | {'Cond(G)':>10} | {'Contr. L':>10} | {'Status'}{RESET}")
        print(f"{'-'*120}")

    best_residual_history = []
    reluctance_network.set_reluctance_at_zero()
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    
    x_k = reluctance_network.magnetic_potential.data.flatten(order='F')[:-1]
    best_pot_data = reluctance_network.magnetic_potential.data.copy()
    best_phi = float('inf') 
    prev_step_norm = None
    
    current_relax = material_relax
    threshold_triggered = False

    def compute_system(x_vec, relax):
        reluctance_network.magnetic_potential.data = np.append(x_vec, 0.0).reshape(mag_pot_shape, order='F')
        reluctance_network.update_reluctance_network(
            magnetic_potential=reluctance_network.magnetic_potential,
            material_relaxation_factor=relax, 
            delta_mu_max=-1 
        )
        comp = reluctance_network.create_magnetic_potential_equation(load_factor=1.0)
        F_x = comp.G.dot(x_vec) - comp.J
        return F_x, comp.G, comp.J

    F_k, G_k, J_k = compute_system(x_k, current_relax)
    B_k = G_k.tocsc() 

    for j in range(1, max_iteration + 1):
        cond_est = float('nan')
        try:
            lu_obj = splu(B_k)
            if debug:
                norm_B = norm(B_k, ord=1)
                inv_op = LinearOperator(B_k.shape, matvec=lu_obj.solve, rmatvec=lu_obj.solve)
                cond_est = norm_B * onenormest(inv_op)
            
            delta_x = -lu_obj.solve(F_k)
        except Exception as e:
            if debug: print(f"{R_c} >>> ERROR: Solver failed ({e}){RESET}")
            break

        x_next = x_k + damping_factor * delta_x
        step_norm_val = np.linalg.norm(delta_x)
        display_step_norm = step_norm_val / (np.linalg.norm(x_k) + 1e-12)

        F_next, G_next, J_next = compute_system(x_next, current_relax)
        phi_true = np.linalg.norm(F_next) / (np.linalg.norm(J_next) + 1e-12)

        contraction_L = float('nan')
        if prev_step_norm is not None and prev_step_norm > 0:
            contraction_L = step_norm_val / prev_step_norm
        prev_step_norm = step_norm_val

        relax_changed = False
        if phi_true < ADAPTIVE_FACTOR_1:
            if not threshold_triggered:
                current_relax = material_relax * ADAPTIVE_FACTOR_2
                threshold_triggered = True
                relax_changed = True
                if debug: print(f"{Y_c} >>> ADAPTIVE: Residual < {ADAPTIVE_FACTOR_1}, Relax halved to {current_relax}{RESET}")
            elif not np.isnan(contraction_L) and contraction_L > 0.9:
                current_relax *= ADAPTIVE_FACTOR_2
                relax_changed = True
                if debug: print(f"{Y_c} >>> ADAPTIVE: L > 0.9, Relax decreased to {current_relax}{RESET}")

        if phi_true < best_phi:
            improvement = best_phi - phi_true
            imp_str = "INIT" if best_phi == float('inf') else f"-{improvement:.2e}"
            best_phi = phi_true
            best_pot_data = reluctance_network.magnetic_potential.data.copy()
            best_residual_history.append(phi_true)
            
            l_color = G_c if (np.isnan(contraction_L) or contraction_L < 1) else R_c
            
            if phi_true <= max_relative_residual:
                status_msg = f"{G_c}CONVERGED!{RESET}"
                if debug:
                    print(f" {j:03d} | {np.linalg.norm(F_next):12.2e} | {phi_true*100:10.6f}% | {best_phi*100:10.6f}% | {display_step_norm:.2e} | {cond_est:.2e} | {l_color}{contraction_L:10.4f}{RESET} | {status_msg}")
                break
            else:
                status_msg = f"{G_c}NEW BEST ({imp_str}){RESET}"
                if debug:
                    print(f" {j:03d} | {np.linalg.norm(F_next):12.2e} | {phi_true*100:10.6f}% | {best_phi*100:10.6f}% | {display_step_norm:.2e} | {cond_est:.2e} | {l_color}{contraction_L:10.4f}{RESET} | {status_msg}")
        else:
            diff = phi_true - best_phi
            best_residual_history.append(phi_true)
            if debug:
                print(f" {j:03d} | {np.linalg.norm(F_next):12.2e} | {phi_true*100:10.6f}% | {best_phi*100:10.6f}% | {display_step_norm:.2e} | {cond_est:.2e} | {R_c}{contraction_L:10.4f}{RESET} | {R_c}WORSENED (+{diff:.2e}){RESET}")
            break

        if relax_changed:
             F_next, G_next, J_next = compute_system(x_next, current_relax)

        B_k = G_next.tocsc() 
        x_k = x_next
        F_k = F_next

    reluctance_network.magnetic_potential.data = best_pot_data
    reluctance_network.add_elements_lite()

    return best_phi, best_residual_history