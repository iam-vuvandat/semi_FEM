import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def fix_point_iteration(reluctance_network, 
                        max_iteration=50, 
                        max_relative_residual=5e-2, 
                        max_backtracking_steps=10, 
                        debug=True):
    
    # --- MÀU SẮC DEBUG ---
    G_c = "\033[92m" # Green (Thành công/Momentum)
    R_c = "\033[91m" # Red (Cảnh báo/Zigzag)
    Y_c = "\033[93m" # Yellow (Thông tin quan trọng)
    C_c = "\033[96m" # Cyan (Process)
    M_c = "\033[95m" # Magenta (Chi tiết toán học)
    RESET = "\033[0m"

    print(f"{C_c}=== BẮT ĐẦU BỘ GIẢI PHI TUYẾN (ULTRA DEBUG MODE) ==={RESET}")

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
            
        print(f"\n{Y_c}------------------------------------------------------------")
        print(f"[TARGET LOAD]: {current_load:.4f}")
        print(f"------------------------------------------------------------{RESET}")

        # --- 1. ENHANCED PREDICTOR ---
        if last_converged_load > 0:
            max_scale = current_load / last_converged_load
            scale_factors = np.linspace(1.0, max_scale, 10)
            best_init_pot, best_init_res = last_reliable_pot.copy(), float('inf')
            
            if debug: print(f"{C_c}[PREDICTOR] Quét 10 điểm nội suy từ {1.0} đến {max_scale:.4f}:{RESET}")
            
            for s in scale_factors:
                temp_p = last_reliable_pot * s
                reluctance_network.magnetic_potential.data = temp_p
                reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                comp_t = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
                
                norm_j_t = np.linalg.norm(comp_t.J) + 1e-12
                res_t = np.linalg.norm(comp_t.G.dot(temp_p.flatten(order='F')[:-1]) - comp_t.J) / norm_j_t
                
                if debug: print(f"  > Scale {s:.3f}: Res = {res_t*100:8.4f}%")
                
                if res_t < best_init_res:
                    best_init_res, best_init_pot = res_t, temp_p.copy()
            
            current_pot = best_init_pot
            if debug: print(f"{G_c}  => Chọn Scale tốt nhất: {s:.4f} (Res: {best_init_res*100:.4f}%){RESET}")
        else:
            current_pot = last_reliable_pot.copy()
        
        converged_this_step = False
        best_res_overall = float('inf')
        last_step_vector = None # Lưu hướng cũ để so sánh
        
        if debug: history_load_markers.append(len(history_residual))

        for j in range(max_iteration):
            # A. Cập nhật vật liệu & Tính Residual cũ
            reluctance_network.magnetic_potential.data = current_pot
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            comp_old = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
            
            p_active_old = current_pot.flatten(order='F')[:-1] 
            norm_j = np.linalg.norm(comp_old.J) + 1e-12
            
            # Tính sai số hiện tại
            residual_vector = comp_old.G.dot(p_active_old) - comp_old.J
            phi_old = np.linalg.norm(residual_vector) / norm_j
            
            if j == 0: best_res_overall = phi_old
            
            # IN TRẠNG THÁI ITERATION
            if debug: 
                print(f"\n{C_c}Iter {j+1:02d} | Start Res: {phi_old*100:10.6f}%{RESET}", end="")

            # B. Giải hệ phương trình (Newton Step)
            p_sol_active = spsolve(comp_old.G, comp_old.J)
            p_sol_full = np.append(p_sol_active, 0.0).reshape(mag_pot_shape, order='F')
            
            # Tính hướng đi thô (Raw Direction)
            raw_direction = p_sol_full - current_pot
            norm_raw = np.linalg.norm(raw_direction)
            if debug: print(f" | Step Size (Raw): {norm_raw:.4e}")

            # ==================================================================
            # C. TÍNH NĂNG ĐIỀU KHIỂN HƯỚNG (CHỈ TẠI LOAD 1.0)
            # ==================================================================
            final_direction = raw_direction
            
            if current_load >= 0.99 and j > 0 and last_step_vector is not None:
                # Tính Cosine Similarity (Góc giữa hướng mới và cũ)
                v_new = raw_direction.flatten()
                v_old = last_step_vector.flatten()
                norm_old = np.linalg.norm(v_old) + 1e-20
                dot_prod = np.dot(v_new, v_old)
                cos_sim = dot_prod / (norm_raw * norm_old + 1e-20)
                
                print(f"{M_c}    [DIRECTION ANALYSIS] Cos(theta) = {cos_sim:.4f}{RESET}")

                if dot_prod < 0:
                    # --- PHÁT HIỆN ZIGZAG (Góc tù) ---
                    print(f"{R_c}    >>> ZIGZAG DETECTED! (Đi ngược hướng cũ){RESET}")
                    
                    # Tính thành phần hình chiếu (Projection)
                    proj_vector = (dot_prod / (norm_old**2)) * last_step_vector
                    
                    # Loại bỏ thành phần song song => Lấy thành phần vuông góc
                    perp_vector = raw_direction - proj_vector
                    norm_perp = np.linalg.norm(perp_vector)
                    
                    print(f"    >>> Correction: Orthogonalizing... (Removed {np.linalg.norm(proj_vector):.4e} magnitude)")
                    final_direction = perp_vector
                else:
                    # --- HƯỚNG THUẬN LỢI (Góc nhọn) ---
                    print(f"{G_c}    >>> ALIGNED! (Đi cùng hướng cũ) -> Adding Momentum{RESET}")
                    momentum_dir = raw_direction + 0.2 * last_step_vector
                    final_direction = momentum_dir
            
            # Lưu hướng lại cho vòng sau
            last_step_vector = final_direction.copy()
            direction = final_direction

            # ==================================================================
            # D. LINE SEARCH (Detailed)
            # ==================================================================
            def evaluate_alpha(a):
                p_t = current_pot + a * direction
                reluctance_network.magnetic_potential.data = p_t
                reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                comp_t = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
                res = np.linalg.norm(comp_t.G.dot(p_t.flatten(order='F')[:-1]) - comp_t.J) / norm_j
                return res, p_t

            if debug: print(f"    [Line Search] Scanning...", end="")
            
            # 1. Coarse Scan
            alphas = np.linspace(0.0, 1.0, 10)
            ls_results = []
            best_coarse_res = float('inf')
            
            for a in alphas:
                if a == 0 and j > 0: continue
                r, p = evaluate_alpha(a)
                ls_results.append((r, p, a))
                if r < best_coarse_res: best_coarse_res = r
            
            b_idx = np.argmin([d[0] for d in ls_results])
            phi_ls, pot_ls, a_ls = ls_results[b_idx]
            
            if debug: print(f" Best Coarse: a={a_ls:.2f} (Res: {phi_ls*100:.4f}%)")

            # 2. Local Scan
            delta = 1.0 / 9.0
            local_alphas = np.linspace(max(0, a_ls - delta/2), min(1.0, a_ls + delta/2), 6)
            for a_loc in local_alphas:
                r_loc, p_loc = evaluate_alpha(a_loc)
                if r_loc < phi_ls:
                    phi_ls, pot_ls, a_ls = r_loc, p_loc, a_loc
            
            # 3. Backtracking check
            if current_load < 1.0 and phi_ls >= phi_old:
                 if debug: print(f"{R_c}    [BACKTRACKING] Residual increased! Halving alpha...{RESET}")
                 temp_a = a_ls
                 count = 0
                 while phi_ls >= phi_old and count < max_backtracking_steps:
                     temp_a /= 2
                     phi_ls, pot_ls = evaluate_alpha(temp_a)
                     a_ls = temp_a
                     count += 1
                     if debug: print(f"      -> Try a={temp_a:.4e} | Res={phi_ls*100:.6f}%")

            # E. CẬP NHẬT VÀ KIỂM TRA HỘI TỤ
            if phi_ls < best_res_overall:
                improvement = best_res_overall - phi_ls
                current_pot = pot_ls.copy()
                best_res_overall = phi_ls
                history_residual.append(phi_ls)
                
                if current_load == 1.0 and phi_ls < best_res_at_final:
                    best_res_at_final, best_pot_at_final = phi_ls, pot_ls.copy()
                
                if debug: 
                    print(f"{G_c}    => ACCEPT: Alpha={a_ls:.4f} | New Res={phi_ls*100:.6f}% (Improv: {improvement*100:.6f}%){RESET}")
                
                if phi_ls < max_relative_residual:
                    converged_this_step = True
                    if debug: print(f"{G_c}    >>> CONVERGED! <<< {RESET}")
                    break
            else:
                if debug: print(f"{R_c}    => STAGNATION: Cannot reduce residual further.{RESET}")
                break 

        # --- KẾT THÚC STEP ---
        if converged_this_step:
            last_reliable_pot, last_converged_load = current_pot.copy(), current_load
            if debug: print(f"{G_c}[SUCCESS] Load {current_load} completed.{RESET}")
        else:
            attempt = load_attempt_count.get(current_load, 0)
            if current_load == 1.0:
                if debug: print(f"{Y_c}[WARNING] Load 1.0 did not strictly converge. Keeping best result.{RESET}")
                load_queue = [] 
            elif attempt < 1:
                mid_load = (last_converged_load + current_load) / 2
                load_attempt_count[current_load] = attempt + 1
                load_queue.insert(0, current_load)
                load_queue.insert(0, mid_load)
                if debug: print(f"{Y_c}[SPLIT] Adding intermediate step: {mid_load:.4f}{RESET}")
            else:
                last_reliable_pot, last_converged_load = current_pot.copy(), current_load
                if debug: print(f"{R_c}[FORCED] Moving forward anyway.{RESET}")

    # --- KẾT THÚC HÀM ---
    reluctance_network.magnetic_potential.data = best_pot_at_final if best_pot_at_final is not None else last_reliable_pot
    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
    reluctance_network.add_elements_lite()

    if debug and history_residual:
        plt.figure(figsize=(12, 7))
        plt.semilogy(history_residual, 'b-o', markersize=4, linewidth=1, label='Residual')
        for marker in history_load_markers:
            plt.axvline(x=marker, color='red', linestyle='--', alpha=0.3)
        plt.axhline(y=max_relative_residual, color='green', linestyle=':', label='Tolerance')
        plt.title('Convergence History (Detailed View)', fontsize=14)
        plt.xlabel('Iterations', fontsize=12)
        plt.ylabel('Relative Residual (Log Scale)', fontsize=12)
        plt.grid(True, which="both", alpha=0.2)
        plt.legend()
        plt.tight_layout()
        plt.show()

    return reluctance_network