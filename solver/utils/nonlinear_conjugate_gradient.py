import numpy as np
import matplotlib.pyplot as plt

def nonlinear_conjugate_gradient(reluctance_network, 
                                 max_iteration=200, # NLCG cần nhiều bước hơn Newton
                                 max_relative_residual=1e-3, # Giảm xuống để đảm bảo độ chính xác
                                 max_backtracking_steps=10, 
                                 debug=True):
    
    # Reset và chuẩn bị dữ liệu ban đầu
    reluctance_network.set_reluctance_at_zero()
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    last_reliable_pot = reluctance_network.magnetic_potential.data.copy()
    last_converged_load = 0.0
    
    # Hàng đợi tải: Bước nhảy nhỏ ở vùng bão hòa (0.9 -> 1.0)
    load_queue = [0.1, 0.4, 0.7, 0.8, 0.9, 0.95, 1.0]
    
    load_attempt_count = {}
    history_residual = []
    history_load_markers = []
    
    # Biến lưu kết quả tốt nhất toàn cục
    best_pot_at_final = None
    best_res_at_final = float('inf')

    # Mã màu debug
    G_c, R_c, Y_c, C_c, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[0m"

    while load_queue:
        current_load = load_queue.pop(0)
        
        # Bỏ qua nếu tải này đã hội tụ
        if current_load <= last_converged_load:
            continue
            
        # ======================================================================
        # 1. ENHANCED PREDICTOR (GIỮ NGUYÊN)
        # ======================================================================
        if last_converged_load > 0:
            max_scale = current_load / last_converged_load
            scale_factors = np.linspace(1.0, max_scale, 10)
            best_init_pot, best_init_res = last_reliable_pot.copy(), float('inf')
            
            if debug: print(f"\n{Y_c}[PREDICTOR] Deep Interpolation Scan for Load: {current_load:.4f}{RESET}")
            
            for s in scale_factors:
                temp_p = last_reliable_pot * s
                reluctance_network.magnetic_potential.data = temp_p
                # Cần update mạng để tính G chuẩn
                reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                comp_t = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
                
                # Tính Residual trực tiếp (r = J - G*A)
                res_vec = comp_t.J - comp_t.G.dot(temp_p.flatten(order='F')[:-1])
                norm_j_t = np.linalg.norm(comp_t.J) + 1e-12
                res_t = np.linalg.norm(res_vec) / norm_j_t
                
                if res_t < best_init_res:
                    best_init_res, best_init_pot = res_t, temp_p.copy()
            
            current_pot = best_init_pot.copy()
            if debug: print(f"  {G_c}  => Best starting factor: {s:.4f} | Res: {best_init_res*100:.6f}%{RESET}")
        else:
            current_pot = last_reliable_pot.copy()
        
        # ======================================================================
        # 2. NONLINEAR CONJUGATE GRADIENT CORE
        # ======================================================================
        converged_this_step = False
        best_res_step = float('inf')
        
        # Khởi tạo biến lưu trữ cho CG
        r_old = None # Residual cũ
        d_old = None # Hướng cũ
        
        if debug:
            print(f"\n{C_c}[NLCG] Polak-Ribiere Optimization | Target Load: {current_load:.4f}{RESET}")
            history_load_markers.append(len(history_residual))

        for j in range(max_iteration):
            # A. Cập nhật trạng thái vật liệu tại điểm hiện tại
            reluctance_network.magnetic_potential.data = current_pot
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            comp = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
            
            # Lấy vector thế từ (active nodes only)
            p_active = current_pot.flatten(order='F')[:-1] 
            
            # B. Tính Residual (Gradient âm): r = J - G*A
            r_vec = comp.J - comp.G.dot(p_active)
            norm_j = np.linalg.norm(comp.J) + 1e-12
            phi_curr = np.linalg.norm(r_vec) / norm_j
            
            if j == 0: best_res_step = phi_curr
            if debug: print(f"  Iter {j+1:3d} | Residual: {phi_curr*100:10.6f}%", end="")

            # C. Kiểm tra hội tụ
            if phi_curr < max_relative_residual:
                if debug: print(f" {G_c}[Converged]{RESET}")
                converged_this_step = True
                history_residual.append(phi_curr)
                break

            # D. Tính Beta và Hướng tìm kiếm (Direction)
            if j == 0 or r_old is None:
                # Bước đầu: Hướng đi là hướng dốc nhất (Steepest Descent)
                d_vec = r_vec.copy()
                beta = 0.0
            else:
                # Polak-Ribière Formula
                diff = r_vec - r_old
                numerator = np.dot(r_vec, diff)
                denominator = np.dot(r_old, r_old) + 1e-20 # Bảo vệ chia cho 0
                
                beta = numerator / denominator
                
                # Restart Strategy: Reset nếu beta âm (hướng xấu)
                beta = max(0, beta) 
                
                # Cập nhật hướng: d_new = r_new + beta * d_old
                d_vec = r_vec + beta * d_old
                
                # Restart nếu hướng tìm kiếm không còn là hướng xuống dốc (Descent direction check)
                # Góc giữa Gradient (-r) và hướng đi (d) phải nhọn
                if np.dot(r_vec, d_vec) <= 0:
                     if debug: print(f" [Restart]", end="")
                     d_vec = r_vec.copy()
                     beta = 0.0

            if debug: print(f" | Beta: {beta:.4f}", end="")

            # Lưu trạng thái cho vòng sau
            r_old = r_vec.copy()
            d_old = d_vec.copy()

            # E. Chuẩn bị vector hướng đầy đủ (thêm nút tham chiếu)
            # [QUAN TRỌNG] Chuẩn hóa d_vec để Alpha có ý nghĩa vật lý
            d_norm_val = np.max(np.abs(d_vec)) + 1e-20
            d_vec_normalized = d_vec / d_norm_val
            direction_full = np.append(d_vec_normalized, 0.0).reshape(mag_pot_shape, order='F')

            # F. Line Search (Hàm cục bộ tối ưu)
            def evaluate_alpha(a):
                # Update: A_new = A_curr + alpha * Direction_normalized
                p_t = current_pot + a * direction_full
                
                # Cập nhật vật liệu tạm thời
                reluctance_network.magnetic_potential.data = p_t
                reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                comp_t = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
                
                # Tính Residual mới
                res_v = comp_t.J - comp_t.G.dot(p_t.flatten(order='F')[:-1])
                return np.linalg.norm(res_v) / norm_j, p_t

            # Quét Alpha: Do đã chuẩn hóa vector hướng, Alpha bây giờ là biên độ thay đổi thế từ (Volt)
            # Quét từ rất nhỏ (1e-4) đến khá lớn (50% giá trị hiện tại)
            current_max_pot = np.max(np.abs(current_pot)) + 1.0
            alphas = np.logspace(-4, np.log10(current_max_pot * 0.5), 8) 
            
            ls_results = []
            for a in alphas:
                r, p = evaluate_alpha(a)
                ls_results.append((r, p, a))
            
            # Chọn Alpha tốt nhất
            b_idx = np.argmin([x[0] for x in ls_results])
            phi_ls, pot_ls, a_ls = ls_results[b_idx]
            
            # Refine Local (Quét tinh)
            if a_ls > 1e-5:
                local_alphas = np.linspace(a_ls * 0.5, a_ls * 1.5, 5)
                for a_loc in local_alphas:
                    r_loc, p_loc = evaluate_alpha(a_loc)
                    if r_loc < phi_ls:
                        phi_ls, pot_ls, a_ls = r_loc, p_loc, a_loc
            
            if debug: print(f" | Alpha: {a_ls:.2e} | New Res: {phi_ls*100:.4f}%")

            # G. Cập nhật nghiệm chính thức
            if phi_ls < best_res_step:
                current_pot = pot_ls.copy()
                best_res_step = phi_ls
                history_residual.append(phi_ls)
                
                # Lưu Global Best (đề phòng fail ở bước cuối)
                if current_load == 1.0 and phi_ls < best_res_at_final:
                    best_res_at_final = phi_ls
                    best_pot_at_final = pot_ls.copy()
                
                # Kiểm tra hội tụ sau Line Search
                if phi_ls < max_relative_residual:
                    converged_this_step = True
                    if debug: print(f"  {G_c}>>> Converged after LS at Iter {j+1}{RESET}")
                    break
            else:
                # Stagnation check: Nếu không giảm được lỗi dù đã thử đủ cách
                if a_ls < 1e-6:
                    if debug: print(f"  {R_c}Stagnation. Resetting direction.{RESET}")
                    r_old = None # Force restart next iter
        
        # ======================================================================
        # 3. SPLIT LOAD & BACKTRACKING (GIỮ NGUYÊN)
        # ======================================================================
        if converged_this_step:
            last_reliable_pot = current_pot.copy()
            last_converged_load = current_load
            if debug: print(f"   {G_c}✓ Success: Load step {current_load:.4f} converged.{RESET}")
        else:
            attempt = load_attempt_count.get(current_load, 0)
            if current_load == 1.0:
                if debug: print(f"{Y_c}[FINAL] Load 1.0 tolerance not met. Saving best result available.{RESET}")
                # Không clear queue, chỉ break để chấp nhận kết quả tương đối
                load_queue = [] 
            elif attempt < 1:
                mid_load = (last_converged_load + current_load) / 2
                load_attempt_count[current_load] = attempt + 1
                load_queue.insert(0, current_load) # Đẩy lại current
                load_queue.insert(0, mid_load)     # Chèn mid vào trước
                if debug: print(f"   {Y_c}[SPLIT] Adaptive backstep to {mid_load:.4f}{RESET}")
            else:
                # Nếu đã chia nhỏ mà vẫn fail, chấp nhận đi tiếp (Forced March)
                last_reliable_pot = current_pot.copy()
                last_converged_load = current_load
                if debug: print(f"   {R_c}[FORCED] Moving forward with best residual ({best_res_step*100:.2f}%).{RESET}")

    # Kết thúc: Gán kết quả tốt nhất
    reluctance_network.magnetic_potential.data = best_pot_at_final if best_pot_at_final is not None else last_reliable_pot
    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
    reluctance_network.add_elements_lite()

    # Vẽ biểu đồ hội tụ
    if debug and history_residual:
        plt.figure(figsize=(10, 6))
        plt.semilogy(history_residual, 'b-o', markersize=3, linewidth=1, label='NLCG Residual')
        for marker in history_load_markers:
            plt.axvline(x=marker, color='red', linestyle='--', alpha=0.3)
        plt.axhline(y=max_relative_residual, color='green', linestyle=':', label='Tolerance')
        plt.title(f'Nonlinear Conjugate Gradient Convergence (Final Res: {history_residual[-1]*100:.4f}%)')
        plt.xlabel('Iterations')
        plt.ylabel('Residual (Log Scale)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    return reluctance_network