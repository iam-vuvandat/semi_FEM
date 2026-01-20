import numpy as np
from scipy.sparse.linalg import spsolve, norm, onenormest, splu, LinearOperator

def fix_point_iteration_for_magnetic_potential(reluctance_network, 
                                               max_iteration=50,
                                               max_relative_residual = 0.05, # Ngưỡng hội tụ mục tiêu
                                               material_relax=0.2, 
                                               damping_factor = 0.1,   
                                               debug = True):
    
    G_c, Y_c, R_c, C_c, B_c, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[96m", "\033[94m", "\033[0m"

    if debug: 
        print(f"\n{Y_c}{'='*110}")
        print(f" FIXED POINT ITERATION (Strict Monotonic + Convergence Goal)")
        print(f" Relax: {material_relax} | Damping: {damping_factor} | Target Res: {max_relative_residual*100}%")
        print(f"{'='*110}{RESET}")
        print(f"{B_c}{'Iter':>4} | {'Step Res':>12} | {'Curr Res':>12} | {'Best Res':>12} | {'Step Norm':>10} | {'Cond(G)':>10} | {'Contr. L':>10} | {'Status'}{RESET}")
        print(f"{'-'*110}")

    best_residual_history = []
    reluctance_network.set_reluctance_at_zero()
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    best_pot_data = reluctance_network.magnetic_potential.data.copy()
    best_phi = float('inf') 
    
    prev_raw_step_norm = None

    for j in range(1, max_iteration + 1):
        reluctance_network.update_reluctance_network(
            magnetic_potential=reluctance_network.magnetic_potential,
            material_relaxation_factor=material_relax, 
            delta_mu_max=-1 
        )
        
        comp = reluctance_network.create_magnetic_potential_equation(load_factor=1.0)
        p_current_active = reluctance_network.magnetic_potential.data.flatten(order='F')[:-1]

        cond_est = float('nan')
        try:
            # Ước tính số điều kiện ma trận để chẩn đoán độ ổn định
            norm_g = norm(comp.G, ord=1)
            lu_obj = splu(comp.G.tocsc())
            
            if debug:
                def solve_op(x): return lu_obj.solve(x)
                inv_op = LinearOperator(comp.G.shape, matvec=solve_op, rmatvec=solve_op)
                norm_inv_g = onenormest(inv_op)
                cond_est = norm_g * norm_inv_g
            
            p_target_active = lu_obj.solve(comp.J)
        except:
            try:
                p_target_active = spsolve(comp.G, comp.J)
            except:
                if debug: print(f"{R_c}>>> FATAL: Linear Solver Failed.{RESET}")
                break

        # Sai số hệ thống tuyến tính (Linear Residual)
        raw_res_vec = comp.J - comp.G.dot(p_target_active)
        step_res = np.linalg.norm(raw_res_vec) / (np.linalg.norm(comp.J) + 1e-12)

        current_raw_step = p_target_active - p_current_active
        current_raw_step_norm = np.linalg.norm(current_raw_step)
        
        # Tính hệ số co (Contraction Factor)
        contraction_L = float('nan')
        if prev_raw_step_norm is not None and prev_raw_step_norm > 0:
            contraction_L = current_raw_step_norm / prev_raw_step_norm
        
        prev_raw_step_norm = current_raw_step_norm
        display_step_norm = current_raw_step_norm / (np.linalg.norm(p_current_active) + 1e-12)
        
        # Cập nhật nghiệm có damping
        p_new_active = p_current_active + damping_factor * current_raw_step
        reluctance_network.magnetic_potential.data = np.append(p_new_active, 0.0).reshape(mag_pot_shape, order='F')

        # Cập nhật lại mạng để tính sai số phi tuyến thực tế (phi_true)
        reluctance_network.update_reluctance_network(
            magnetic_potential=reluctance_network.magnetic_potential,
            material_relaxation_factor=1.0, 
            delta_mu_max=-1
        )
        v_comp = reluctance_network.create_magnetic_potential_equation(load_factor=1.0)
        
        res_vector = v_comp.J - v_comp.G.dot(p_new_active)
        phi_true = np.linalg.norm(res_vector) / (np.linalg.norm(v_comp.J) + 1e-12)

        # Logic kiểm tra hội tụ và monotonicity
        if phi_true < best_phi:
            improvement = best_phi - phi_true
            imp_str = "INIT" if best_phi == float('inf') else f"-{improvement:.2e}"
            
            best_phi = phi_true
            best_pot_data = reluctance_network.magnetic_potential.data.copy()
            best_residual_history.append(phi_true)
            
            # Kiểm tra xem đã đạt mục tiêu chưa
            if phi_true <= max_relative_residual:
                status_msg = f"{G_c}CONVERGED!{RESET}"
                if debug:
                    l_color = G_c if (np.isnan(contraction_L) or contraction_L < 1) else R_c
                    print(f" {j:03d} | {step_res:12.2e} | {phi_true*100:10.6f}% | {best_phi*100:10.6f}% | {display_step_norm:.2e} | {cond_est:.2e} | {l_color}{contraction_L:10.4f}{RESET} | {status_msg}")
                break
            else:
                status_msg = f"{G_c}NEW BEST ({imp_str}){RESET}"
            
            if debug:
                l_color = G_c if (np.isnan(contraction_L) or contraction_L < 1) else R_c
                print(f" {j:03d} | {step_res:12.2e} | {phi_true*100:10.6f}% | {best_phi*100:10.6f}% | {display_step_norm:.2e} | {cond_est:.2e} | {l_color}{contraction_L:10.4f}{RESET} | {status_msg}")
        else:
            # Nếu sai số tăng: Dừng ngay lập tức để tránh nổ nghiệm
            diff = phi_true - best_phi
            best_residual_history.append(phi_true)
            
            if debug:
                print(f" {j:03d} | {step_res:12.2e} | {phi_true*100:10.6f}% | {best_phi*100:10.6f}% | {display_step_norm:.2e} | {cond_est:.2e} | {R_c}{contraction_L:10.4f}{RESET} | {R_c}WORSENED (+{diff:.2e}){RESET}")
                print(f"\n{Y_c}>>> STOPPED EARLY: Reverting to best result (Residual: {best_phi*100:.4f}%).{RESET}")
            break

    # Trả về kết quả tốt nhất tìm được
    reluctance_network.magnetic_potential.data = best_pot_data
    reluctance_network.add_elements_lite()

    return best_phi, best_residual_history