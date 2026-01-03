import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def nonlinear_conjugate_gradient(reluctance_network, 
                           max_iteration=100, 
                           max_relative_residual=5e-2, 
                           max_backtracking_steps=10, 
                           debug=True):
    """
    Bộ giải lai (Hybrid Solver) tối ưu cho máy cấu hình giới hạn (8GB RAM).
    - Tải thấp (< 0.9): Dùng Newton-Raphson (Nhanh, ít lặp).
    - Tải cao (>= 0.9): Dùng Preconditioned NLCG (Ổn định, không tốn RAM, trị dao động).
    """
    
    # --- MÀU SẮC DEBUG ---
    G_c = "\033[92m" # Green: Thành công
    M_c = "\033[95m" # Magenta: Chế độ NLCG
    Y_c = "\033[93m" # Yellow: Cảnh báo/Predictor
    C_c = "\033[96m" # Cyan: Thông tin
    RESET = "\033[0m"

    print(f"{C_c}=== HYBRID SOLVER: NEWTON (Early) + PRECONDITIONED NLCG (Saturation) ==={RESET}")

    reluctance_network.set_reluctance_at_zero()
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    last_reliable_pot = reluctance_network.magnetic_potential.data.copy()
    last_converged_load = 0.0
    
    # Hàng đợi tải
    load_queue = [0.1, 0.4, 0.7, 0.8, 0.9, 0.95, 1.0]
    
    load_attempt_count = {}
    history_residual = []
    history_load_markers = []
    best_pot_at_final = None
    best_res_at_final = float('inf')

    while load_queue:
        current_load = load_queue.pop(0)
        if current_load <= last_converged_load:
            continue
            
        # --- CHIẾN THUẬT CHUYỂN MODE ---
        # Sửa: Chuyển sang NLCG ngay từ 0.9 để tránh dao động ở 0.95
        SOLVER_MODE = "NLCG" if current_load >= 0.90 else "NEWTON"
        mode_color = M_c if SOLVER_MODE == "NLCG" else G_c
        
        print(f"\n{Y_c}------------------------------------------------------------")
        print(f"[TARGET LOAD]: {current_load:.4f} | MODE: {mode_color}{SOLVER_MODE} (Jacobi){Y_c}")
        print(f"------------------------------------------------------------{RESET}")

        # --- 1. ENHANCED PREDICTOR ---
        if last_converged_load > 0:
            max_scale = current_load / last_converged_load
            scale_factors = np.linspace(1.0, max_scale, 10)
            best_init_pot, best_init_res = last_reliable_pot.copy(), float('inf')
            
            if debug: print(f"{C_c}[PREDICTOR] Scanning...{RESET}")
            for s in scale_factors:
                temp_p = last_reliable_pot * s
                reluctance_network.magnetic_potential.data = temp_p
                reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                comp_t = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
                
                # Tính nhanh Residual
                res_vec = comp_t.J - comp_t.G.dot(temp_p.flatten(order='F')[:-1])
                res_t = np.linalg.norm(res_vec) / (np.linalg.norm(comp_t.J)+1e-12)
                
                if res_t < best_init_res: best_init_res, best_init_pot = res_t, temp_p.copy()
            current_pot = best_init_pot
            if debug: print(f"  => Best Scale: {s:.4f} (Res: {best_init_res*100:.2f}%)")
        else:
            current_pot = last_reliable_pot.copy()
        
        converged_this_step = False
        best_res_overall = float('inf')
        
        # Biến trạng thái riêng cho NLCG
        nlcg_r_old = None
        nlcg_z_old = None # Vector Gradient đã điều kiện hóa
        nlcg_d_old = None
        
        if debug: history_load_markers.append(len(history_residual))

        for j in range(max_iteration):
            # Cập nhật vật liệu & ma trận
            reluctance_network.magnetic_potential.data = current_pot
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            comp = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
            
            p_active = current_pot.flatten(order='F')[:-1] 
            norm_j = np.linalg.norm(comp.J) + 1e-12
            
            # Tính Residual hiện tại: r = J - G*A
            residual_vec = comp.J - comp.G.dot(p_active)
            phi_curr = np.linalg.norm(residual_vec) / norm_j
            
            if j == 0: best_res_overall = phi_curr
            if debug: print(f"  Iter {j+1:02d} | Res: {phi_curr*100:9.6f}%", end="")
            
            if phi_curr < max_relative_residual:
                converged_this_step = True
                if debug: print(f" {G_c}[Converged]{RESET}")
                history_residual.append(phi_curr)
                break

            # ==================================================================
            # LÕI THUẬT TOÁN: RẼ NHÁNH TẠI ĐÂY
            # ==================================================================
            direction_full = None
            
            if SOLVER_MODE == "NEWTON":
                # --- NEWTON-RAPHSON (Giải trực tiếp) ---
                # Nhanh nhưng tốn RAM, dễ dao động ở tải cao
                p_sol_active = spsolve(comp.G, comp.J)
                p_sol_full = np.append(p_sol_active, 0.0).reshape(mag_pot_shape, order='F')
                direction_full = p_sol_full - current_pot
                
                if debug: print(f" | {G_c}Newton{RESET}", end="")

            else: 
                # --- PRECONDITIONED NLCG (Jacobi) ---
                # Ổn định, tiết kiệm RAM, trị dao động
                
                # 1. Tạo Tiền điều kiện Jacobi (M^-1 ~ 1/diag(G))
                diag_G = comp.G.diagonal()
                M_inv = 1.0 / (diag_G + 1e-25) # Thêm epsilon bảo vệ chia 0
                
                r_vec = residual_vec # Gradient âm
                
                # 2. Áp dụng Preconditioner: z = M^-1 * r
                # Biến đổi không gian để "làm tròn" mặt năng lượng
                z_vec = r_vec * M_inv
                
                if j == 0 or nlcg_r_old is None:
                    d_vec = z_vec.copy()
                    beta = 0.0
                    if debug: print(f" | {M_c}PNLCG Init{RESET}", end="")
                else:
                    # 3. Tính Beta (Polak-Ribière)
                    diff_z = z_vec - nlcg_z_old
                    numerator = np.dot(r_vec, diff_z)
                    denominator = np.dot(nlcg_r_old, nlcg_z_old) + 1e-25
                    
                    beta = max(0, numerator / denominator) # Restart nếu beta < 0
                    
                    d_vec = z_vec + beta * nlcg_d_old
                    
                    # Restart nếu hướng tìm kiếm không tốt (Góc tù với Gradient)
                    if np.dot(r_vec, d_vec) <= 0:
                        d_vec = z_vec.copy()
                        beta = 0.0
                        if debug: print(f" | {Y_c}Restart{RESET}", end="")
                    
                    if debug: print(f" | {M_c}Beta: {beta:.2f}{RESET}", end="")

                # Lưu trạng thái
                nlcg_r_old = r_vec.copy()
                nlcg_z_old = z_vec.copy()
                nlcg_d_old = d_vec.copy()
                
                # 4. Chuẩn hóa hướng (Normalization)
                # Quan trọng vì z_vec rất lớn do nhân với 1/G
                d_max = np.max(np.abs(d_vec)) + 1e-25
                d_vec_norm = d_vec / d_max
                
                # Scale hướng đi khoảng 10% biên độ thế từ hiện tại
                scale_guess = np.max(np.abs(current_pot)) * 0.1 
                if scale_guess == 0: scale_guess = 1.0
                
                direction_full = np.append(d_vec_norm, 0.0).reshape(mag_pot_shape, order='F')
                direction_full *= scale_guess

            # ==================================================================
            # LINE SEARCH (Dùng chung)
            # ==================================================================
            def evaluate_alpha(a):
                p_t = current_pot + a * direction_full
                reluctance_network.magnetic_potential.data = p_t
                reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                comp_t = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
                res = np.linalg.norm(comp_t.G.dot(p_t.flatten(order='F')[:-1]) - comp_t.J) / norm_j
                return res, p_t

            # Quét Alpha logarit (Bao phủ cả step nhỏ của NLCG và step đơn vị của Newton)
            alphas = np.logspace(-3, 0.1, 10) 
            
            ls_results = []
            for a in alphas:
                r, p = evaluate_alpha(a)
                ls_results.append((r, p, a))
            
            b_idx = np.argmin([d[0] for d in ls_results])
            phi_ls, pot_ls, a_ls = ls_results[b_idx]
            
            # Local Refine (Quét tinh)
            if a_ls > 1e-4:
                local_alphas = np.linspace(a_ls * 0.5, a_ls * 1.5, 5)
                for a_loc in local_alphas:
                    r_loc, p_loc = evaluate_alpha(a_loc)
                    if r_loc < phi_ls: phi_ls, pot_ls, a_ls = r_loc, p_loc, a_loc

            if debug: print(f" | Alpha: {a_ls:.1e} -> NewRes: {phi_ls*100:.4f}%")

            # Cập nhật kết quả bước
            if phi_ls < best_res_overall:
                current_pot = pot_ls.copy()
                best_res_overall = phi_ls
                history_residual.append(phi_ls)
                
                if current_load == 1.0 and phi_ls < best_res_at_final:
                    best_res_at_final, best_pot_at_final = phi_ls, pot_ls.copy()
                
                if phi_ls < max_relative_residual:
                    converged_this_step = True
                    break
            else:
                # Nếu bế tắc (Stagnation)
                if SOLVER_MODE == "NLCG" and a_ls < 1e-6:
                     nlcg_r_old = None # Reset NLCG

        # --- XỬ LÝ KẾT THÚC BƯỚC TẢI ---
        if converged_this_step:
            last_reliable_pot, last_converged_load = current_pot.copy(), current_load
            if debug: print(f"{G_c}[DONE] Step {current_load} converged.{RESET}")
        else:
            attempt = load_attempt_count.get(current_load, 0)
            if current_load == 1.0:
                if debug: print(f"{Y_c}[FINAL] Load 1.0 stop. Saving best result.{RESET}")
                load_queue = [] 
            elif attempt < 1:
                mid_load = (last_converged_load + current_load) / 2
                load_attempt_count[current_load] = attempt + 1
                load_queue.insert(0, current_load)
                load_queue.insert(0, mid_load)
                if debug: print(f"{Y_c}[SPLIT] Backstep -> {mid_load:.4f}{RESET}")
            else:
                last_reliable_pot, last_converged_load = current_pot.copy(), current_load
                if debug: print(f"{Y_c}[SKIP] Force continue.{RESET}")

    # Kết thúc hàm
    reluctance_network.magnetic_potential.data = best_pot_at_final if best_pot_at_final is not None else last_reliable_pot
    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
    reluctance_network.add_elements_lite()
    
    if debug and history_residual:
        plt.figure(figsize=(10, 6))
        plt.semilogy(history_residual, 'b-o', markersize=4, label='Residual')
        for m in history_load_markers: plt.axvline(x=m, color='r', linestyle='--', alpha=0.3)
        plt.axhline(y=max_relative_residual, color='g', linestyle=':')
        plt.title('Hybrid Solver Convergence History')
        plt.legend()
        plt.show()

    return reluctance_network