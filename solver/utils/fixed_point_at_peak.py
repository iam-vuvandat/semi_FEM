import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def fixed_point_at_peak(reluctance_network, 
                        max_iteration=50, 
                        max_relative_residual=5e-2, 
                        max_backtracking_steps=10, 
                        debug=True):
    
    reluctance_network.set_minimum_reluctance()
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    last_reliable_pot = reluctance_network.magnetic_potential.data.copy()
    last_converged_load = 0.0
    load_queue = [1.0]
    
    load_attempt_count = {}
    history_residual = []
    history_load_markers = []
    best_pot_at_final = None
    best_res_at_final = float('inf')

    G_c, R_c, Y_c, C_c, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[0m"

    while load_queue:
        current_load = load_queue.pop(0)
        if current_load <= last_converged_load:
            continue
            
        # --- ENHANCED PREDICTOR (10-point Linear Interpolation) ---
        if last_converged_load > 0:
            max_scale = current_load / last_converged_load
            # Scanning 10 interpolation coefficients for a better starting point
            scale_factors = np.linspace(1.0, max_scale, 10)
            best_init_pot, best_init_res = last_reliable_pot.copy(), float('inf')
            
            if debug:
                print(f"\n{Y_c}[PREDICTOR] Deep Interpolation Scan for Load: {current_load:.4f}{RESET}")
            
            for s in scale_factors:
                temp_p = last_reliable_pot * s
                reluctance_network.magnetic_potential.data = temp_p
                reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                comp_t = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
                
                norm_j_t = np.linalg.norm(comp_t.J) + 1e-12
                res_t = np.linalg.norm(comp_t.G.dot(temp_p.flatten(order='F')[:-1]) - comp_t.J) / norm_j_t
                
                if debug:
                    print(f"    * Interpolation Factor: {s:8.4f} | Residual: {res_t*100:10.6f}%")
                
                if res_t < best_init_res:
                    best_init_res, best_init_pot = res_t, temp_p.copy()
            
            current_pot = best_init_pot
            if debug:
                print(f"  {G_c}  => Selected best starting factor: {s:.4f} with Res: {best_init_res*100:.6f}%{RESET}")
        else:
            current_pot = last_reliable_pot.copy()
        
        converged_this_step = False
        best_res_overall = float('inf')
        
        if debug:
            print(f"\n{C_c}[PROCESS] Correcting Nonlinear System | Target Load: {current_load:.4f}{RESET}")
            history_load_markers.append(len(history_residual))

        for j in range(max_iteration):
            reluctance_network.magnetic_potential.data = current_pot
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            comp_old = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
            
            p_active_old = current_pot.flatten(order='F')[:-1] 
            norm_j = np.linalg.norm(comp_old.J) + 1e-12
            phi_old = np.linalg.norm(comp_old.G.dot(p_active_old) - comp_old.J) / norm_j
            
            if j == 0: best_res_overall = phi_old
            if debug: print(f"  Iteration {j+1:2d} | Residual: {phi_old*100:10.6f}%")

            p_sol_active = spsolve(comp_old.G, comp_old.J)
            p_sol_full = np.append(p_sol_active, 0.0).reshape(mag_pot_shape, order='F')
            direction = p_sol_full - current_pot
            
            def evaluate_alpha(a):
                p_t = current_pot + a * direction
                reluctance_network.magnetic_potential.data = p_t
                reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                comp_t = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
                res = np.linalg.norm(comp_t.G.dot(p_t.flatten(order='F')[:-1]) - comp_t.J) / norm_j
                return res, p_t

            # --- DUAL-PHASE LINE SEARCH (10 Coarse + 6 Local) ---
            alphas = np.linspace(0.0, 1.0, 10)
            ls_results = []
            for a in alphas:
                if a == 0 and j > 0: continue
                r, p = evaluate_alpha(a)
                ls_results.append((r, p, a))
                if debug: print(f"    - Coarse Scan  | Damping: {a:8.4f} | Residual: {r*100:10.6f}%")
            
            b_idx = np.argmin([d[0] for d in ls_results])
            phi_ls, pot_ls, a_ls = ls_results[b_idx]

            delta = 1.0 / 9.0
            local_alphas = np.linspace(max(0, a_ls - delta/2), min(1.0, a_ls + delta/2), 8)
            for a_loc in local_alphas[1:-1]: # 6 inner points
                r_loc, p_loc = evaluate_alpha(a_loc)
                if debug: print(f"    - Local Scan   | Damping: {a_loc:8.4f} | Residual: {r_loc*100:10.6f}%")
                if r_loc < phi_ls:
                    phi_ls, pot_ls, a_ls = r_loc, p_loc, a_loc

            if current_load < 1.0:
                bt_count = 0
                temp_a = a_ls
                while phi_ls >= phi_old and bt_count < max_backtracking_steps and temp_a > 1e-5:
                    temp_a /= 2
                    phi_ls, pot_ls = evaluate_alpha(temp_a)
                    a_ls = temp_a
                    bt_count += 1
                    if debug: print(f"    - Backtrack    | Damping: {a_ls:.4e} | Residual: {phi_ls*100:10.6f}%")

            if phi_ls < best_res_overall:
                current_pot = pot_ls.copy()
                best_res_overall = phi_ls
                history_residual.append(phi_ls)
                
                if current_load == 1.0 and phi_ls < best_res_at_final:
                    best_res_at_final, best_pot_at_final = phi_ls, pot_ls.copy()
                
                if debug: print(f"  {G_c}  => NEW BEST    | Damping: {a_ls:8.4f} | Residual: {phi_ls*100:10.6f}%{RESET}")
                if phi_ls < max_relative_residual:
                    converged_this_step = True
                    break
            else:
                if debug: print(f"  {R_c}  => NO PROGRESS | Local minimum or divergence detected.{RESET}")
                break 

        # --- ONE-TIME SPLIT LOAD POLICY ---
        if converged_this_step:
            last_reliable_pot, last_converged_load = current_pot.copy(), current_load
            if debug: print(f"   {G_c}✓ Success: Load step {current_load:.4f} converged.{RESET}")
        else:
            attempt = load_attempt_count.get(current_load, 0)
            if current_load == 1.0:
                if debug: print(f"{Y_c}[FINAL] Target Load 1.0 failed to meet tolerance. Finalizing.{RESET}")
                load_queue = [] 
            elif attempt < 1:
                mid_load = (last_converged_load + current_load) / 2
                load_attempt_count[current_load] = attempt + 1
                load_queue.insert(0, current_load)
                load_queue.insert(0, mid_load)
                if debug: print(f"   {Y_c}[SPLIT] Adaptive backstep to {mid_load:.4f} (Attempt 1/1).{RESET}")
            else:
                last_reliable_pot, last_converged_load = current_pot.copy(), current_load
                if debug: 
                    print(f"   {R_c}[FORCED] Failed again at {current_load:.4f}. Moving forward with best residual.{RESET}")

    reluctance_network.magnetic_potential.data = best_pot_at_final if best_pot_at_final is not None else last_reliable_pot
    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
    reluctance_network.add_elements_lite()

    if debug and history_residual:
        plt.figure(figsize=(11, 6))
        plt.semilogy(history_residual, 'b-o', markersize=4, linewidth=1, label='Residual Trend')
        for marker in history_load_markers:
            plt.axvline(x=marker, color='red', linestyle='--', alpha=0.3)
        plt.axhline(y=max_relative_residual, color='green', linestyle=':', label='Target Tolerance')
        plt.title('Nonlinear Solver Convergence History (Log-Scale)', fontsize=12)
        plt.xlabel('Successful Update Iterations', fontsize=10)
        plt.ylabel('Relative Residual', fontsize=10)
        plt.grid(True, which="both", alpha=0.2)
        plt.legend()
        plt.tight_layout()
        plt.show()

    return reluctance_network