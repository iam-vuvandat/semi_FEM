import numpy as np
from scipy.sparse.linalg import spsolve, norm, onenormest, splu, LinearOperator

def broyden_iteration_for_magnetic_potential(reluctance_network, 
                                               max_iteration=50,
                                               max_relative_residual=0.05, # Ngưỡng hội tụ mục tiêu
                                               material_relax=0.2, 
                                               damping_factor=0.5,   
                                               debug=True):
    
    # --- Định nghĩa màu sắc log ---
    G_c, Y_c, R_c, C_c, B_c, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[96m", "\033[94m", "\033[0m"

    if debug: 
        print(f"\n{Y_c}{'='*120}")
        print(f" BROYDEN QUASI-NEWTON (Strict Monotonic + Convergence Goal)")
        print(f" Relax: {material_relax} | Damping: {damping_factor} | Target Res: {max_relative_residual*100}%")
        print(f"{'='*120}{RESET}")
        print(f"{B_c}{'Iter':>4} | {'F(x) Norm':>12} | {'Curr Res':>12} | {'Best Res':>12} | {'Step Norm':>10} | {'Cond(G)':>10} | {'Contr. L':>10} | {'Status'}{RESET}")
        print(f"{'-'*120}")

    best_residual_history = []
    reluctance_network.set_reluctance_at_zero()
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    
    # Khởi tạo nghiệm ban đầu
    x_k = reluctance_network.magnetic_potential.data.flatten(order='F')[:-1]
    best_pot_data = reluctance_network.magnetic_potential.data.copy()
    best_phi = float('inf') 
    prev_step_norm = None

    # Hàm hỗ trợ tính toán vector dư F(x) = G*x - J
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

    # Bước 0: Tính Jacobian xấp xỉ ban đầu (B_k) từ ma trận G của Picard
    F_k, G_k, J_k = compute_system(x_k, material_relax)
    B_k = G_k.tocsc() 

    for j in range(1, max_iteration + 1):
        # 1. Ước tính số điều kiện ma trận (Condition Number)
        cond_est = float('nan')
        try:
            lu_obj = splu(B_k)
            if debug:
                norm_B = norm(B_k, ord=1)
                inv_op = LinearOperator(B_k.shape, matvec=lu_obj.solve, rmatvec=lu_obj.solve)
                cond_est = norm_B * onenormest(inv_op)
            
            # 2. Giải tìm bước nhảy Newton: delta_x = - B_k^-1 * F_k
            delta_x = -lu_obj.solve(F_k)
        except Exception as e:
            if debug: print(f"{R_c} >>> ERROR: Solver failed ({e}){RESET}")
            break

        # 3. Cập nhật nghiệm: x_{k+1} = x_k + alpha * delta_x
        x_next = x_k + damping_factor * delta_x
        step_norm_val = np.linalg.norm(delta_x)
        display_step_norm = step_norm_val / (np.linalg.norm(x_k) + 1e-12)

        # 4. Tính toán vector dư mới F_{k+1} và kiểm tra hội tụ phi tuyến thực tế
        F_next, G_next, J_next = compute_system(x_next, material_relax)
        phi_true = np.linalg.norm(F_next) / (np.linalg.norm(J_next) + 1e-12)

        # 5. Tính hệ số co L
        contraction_L = float('nan')
        if prev_step_norm is not None and prev_step_norm > 0:
            contraction_L = step_norm_val / prev_step_norm
        prev_step_norm = step_norm_val

        # 6. Kiểm tra cải thiện (Strict Monotonic Strategy)
        if phi_true < best_phi:
            improvement = best_phi - phi_true
            imp_str = "INIT" if best_phi == float('inf') else f"-{improvement:.2e}"
            best_phi = phi_true
            best_pot_data = reluctance_network.magnetic_potential.data.copy()
            best_residual_history.append(phi_true)
            
            l_color = G_c if (np.isnan(contraction_L) or contraction_L < 1) else R_c
            
            # Kiểm tra đạt mục tiêu hội tụ
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
            # Nếu sai số tăng: Dừng ngay lập tức để bảo vệ nghiệm tốt nhất
            diff = phi_true - best_phi
            best_residual_history.append(phi_true)
            if debug:
                print(f" {j:03d} | {np.linalg.norm(F_next):12.2e} | {phi_true*100:10.6f}% | {best_phi*100:10.6f}% | {display_step_norm:.2e} | {cond_est:.2e} | {R_c}{contraction_L:10.4f}{RESET} | {R_c}WORSENED (+{diff:.2e}){RESET}")
                print(f"\n{Y_c}>>> STOPPED EARLY: Reverting to best result.{RESET}")
            break

        # 7. CẬP NHẬT TRẠNG THÁI CHO BƯỚC TIẾP THEO
        # Restart Jacobian xấp xỉ bằng ma trận G mới để giữ tính ổn định vật lý
        B_k = G_next.tocsc() 
        x_k = x_next
        F_k = F_next

    # Kết thúc: Khôi phục lại trạng thái tốt nhất (phi thấp nhất)
    reluctance_network.magnetic_potential.data = best_pot_data
    reluctance_network.add_elements_lite()

    return best_phi, best_residual_history