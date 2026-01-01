import numpy as np
import matplotlib.pyplot as plt

def nonlinear_conjugate_gradient(reluctance_network,
                                 max_iteration=500, # Jacobi cần nhiều iter hơn để bò về đích
                                 max_relative_residual=1e-4,
                                 load_step=None, 
                                 line_search_max=10,
                                 debug=True):

    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    load_queue = [1.0]
    residual_history = []
    
    last_step_checkpoint = np.zeros(mag_pot_shape)
    last_converged_load = 0.0

    GREEN, RED, WHITE, YELLOW, CYAN, RESET = \
        "\033[92m", "\033[91m", "\033[97m", "\033[93m", "\033[96m", "\033[0m"

    while load_queue:
        current_load = load_queue.pop(0)
        
        # Reset nếu bắt đầu từ 0
        if last_converged_load == 0.0:
            reluctance_network.set_reluctance_at_zero()
            reluctance_network.magnetic_potential.data.fill(0.0)
            last_step_checkpoint = reluctance_network.magnetic_potential.data.copy()
        else:
            reluctance_network.magnetic_potential.data = last_step_checkpoint.copy()
        
        reluctance_network.update_reluctance_network(reluctance_network.magnetic_potential)

        converged_this_step = False
        best_x_this_load = last_step_checkpoint.copy()
        min_res_this_load = float('inf')
        res_history_this_load = []

        for k in range(max_iteration):
            comp = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
            G, J = comp.G, comp.J
            norm_J = np.linalg.norm(J) + 1e-12
            
            x_vec = reluctance_network.magnetic_potential.data.flatten(order='F')
            g = G.dot(x_vec[:-1]) - J
            res_old_norm = np.linalg.norm(g)
            
            # --- CHIẾN THUẬT JACOBI PRECONDITIONER ---
            # Lấy đường chéo của G
            diag_G = G.diagonal()
            # Tránh chia cho 0 (tại các nút biên hoặc nút cô lập)
            diag_G_inv = np.where(np.abs(diag_G) > 1e-20, 1.0 / diag_G, 1.0)
            
            # Hướng đi d = - diag(G)^-1 * g
            z = diag_G_inv * g
            d = -np.append(z, 0.0)

            # --- TẦNG 2: BACKTRACKING LINE SEARCH ---
            alpha = 1.0
            success_ls = False
            for ls_idx in range(line_search_max):
                x_trial = x_vec + alpha * d
                reluctance_network.magnetic_potential.data = x_trial.reshape(mag_pot_shape, order='F')
                
                reluctance_network.update_reluctance_network(reluctance_network.magnetic_potential)
                comp_new = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
                g_new = comp_new.G.dot(x_trial[:-1]) - comp_new.J
                res_new_norm = np.linalg.norm(g_new)
                
                if res_new_norm < res_old_norm:
                    success_ls = True
                    break
                alpha *= 0.5

            res_val = res_new_norm / norm_J
            residual_history.append(res_val)
            res_history_this_load.append(res_val)

            if res_val < min_res_this_load:
                min_res_this_load = res_val
                best_x_this_load = x_trial.reshape(mag_pot_shape, order='F')

            if debug and k % 10 == 0: # Jacobi lặp nhiều nên 10 bước in 1 lần cho đỡ rối
                print(f"{WHITE}L {current_load:.4f} | It {k+1:3d} | Res {res_val*100:8.4f}%{RESET}")

            # CẮT LỖ: Nếu It 2 tăng sai số
            if k == 1 and res_history_this_load[1] > res_history_this_load[0]:
                if debug: print(f"{RED}  [!] Jacobi phân kỳ. Hạ tải ngay...{RESET}")
                break

            if res_val < max_relative_residual:
                last_step_checkpoint = x_trial.reshape(mag_pot_shape, order='F')
                last_converged_load = current_load
                converged_this_step = True
                if abs(current_load - 1.0) > 1e-5: load_queue.append(1.0)
                break
            
            if not success_ls and alpha < 1e-8: break
            x_vec = x_trial

        # --- TẦNG 1: SUB-STEPPING ---
        if not converged_this_step:
            mid_load = 0.5 * (last_converged_load + current_load)
            if abs(current_load - last_converged_load) > 1e-6:
                load_queue.insert(0, current_load)
                load_queue.insert(0, mid_load)
            else:
                last_step_checkpoint = best_x_this_load.copy()
                last_converged_load = current_load
                converged_this_step = True

    reluctance_network.magnetic_potential.data = last_step_checkpoint
    reluctance_network.add_elements_lite()
    return last_step_checkpoint