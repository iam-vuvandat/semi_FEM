import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def fix_point_iteration(reluctance_network, 
                        max_iteration=50, 
                        max_relative_residual=1e-4, 
                        adaptive_damping_factor=(1.0, 0.1),
                        load_step=10, 
                        debug=True):

    reluctance_network.set_reluctance_at_zero()
    if isinstance(max_iteration, tuple): 
        max_iteration = max_iteration[0]

    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()
    
    # Checkpoint lưu nghiệm tốt nhất của bước tải TRƯỚC (Dùng cho Backtrack tầng 2)
    last_step_checkpoint = current_magnetic_potential.copy()
    
    load_factors = np.linspace(0,1,load_step +1)[1:]
    smart_damping = np.linspace(adaptive_damping_factor[0], adaptive_damping_factor[1], load_step)
    
    residual_history = []
    load_step_indices = []

    GREEN, RED, WHITE, YELLOW, RESET = "\033[92m", "\033[91m", "\033[97m", "\033[93m", "\033[0m"

    i = 0
    while i < load_step:
        current_load = load_factors[i]
        initial_step_damping = smart_damping[i]
        
        # --- Logic Backtrack Tầng 2 ---
        l2_retry = 0
        l2_limit = 3 # Tối đa 3 lần thử lại cho mỗi bước tải
        converged_this_step = False
        
        while l2_retry <= l2_limit and not converged_this_step:
            current_damping = initial_step_damping
            backtrack_count = 0
            backtrack_limit = max_iteration // 2
            
            # Reset về nghiệm của bước trước khi bắt đầu thử (hoặc thử lại)
            current_magnetic_potential = last_step_checkpoint.copy()
            reluctance_network.magnetic_potential.data = current_magnetic_potential
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            
            # Cần lưu lại kết quả hội tụ của các iteration để tính Res tầng 1
            local_stable_checkpoint = current_magnetic_potential.copy()
            
            j = 0
            while j < (max_iteration * 2 if i == load_step - 1 else max_iteration):
                if j == 0 and i > 0 and l2_retry == 0:
                    load_step_indices.append(len(residual_history))

                # Giải phương trình
                comp = reluctance_network.create_magnetic_potential_equation(
                    first_time=(i == 0 and j == 0),
                    load_factor=current_load, debug=False
                )
                G_old, J = comp.G, comp.J
                norm_J = np.linalg.norm(J) + 1e-12
                
                p_sol = spsolve(G_old, J)
                p_full = np.append(p_sol, 0.0).reshape(magnetic_potential_shape, order='F')

                # Update với damping
                direction = p_full - current_magnetic_potential
                test_potential = current_magnetic_potential + current_damping * direction
                
                reluctance_network.magnetic_potential.data = test_potential
                reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)

                # Tính Residual
                comp_new = reluctance_network.create_magnetic_potential_equation(
                    first_time=False, load_factor=current_load, debug=False
                )
                P_active = test_potential.flatten(order='F')[:-1]
                res_val = np.linalg.norm(comp_new.G.dot(P_active) - J) / norm_J

                if debug:
                    color = WHITE if j == 0 else (GREEN if (len(residual_history) > 0 and res_val < residual_history[-1]) else RED)
                    retry_str = f" (Retry L2: {l2_retry})" if l2_retry > 0 else ""
                    print(f"{color}Step {i+1}/{load_step}{retry_str}, Iter {j+1}: Damping = {current_damping:.4f}, Res = {res_val*100:.4f}%{RESET}")

                # --- Backtrack Tầng 1 (Trong cùng một bước lặp) ---
                if j > 0 and len(residual_history) > 0:
                    if res_val > residual_history[-1] * 1.01:
                        if backtrack_count < backtrack_limit and current_damping > (0.01 * initial_step_damping):
                            backtrack_count += 1
                            current_magnetic_potential = local_stable_checkpoint.copy()
                            reluctance_network.magnetic_potential.data = current_magnetic_potential
                            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                            current_damping *= 0.5
                            if debug: print(f"   {RED}[!] Backtrack L1 {backtrack_count}. Damping -> {current_damping:.4f}{RESET}")
                            continue
                        else:
                            # Thất bại tầng 1 -> Thoát vòng lặp j để xử lý tầng 2
                            break

                # Lưu nghiệm tạm thời cho iteration tiếp theo
                local_stable_checkpoint = test_potential.copy()
                current_magnetic_potential = test_potential.copy()
                residual_history.append(res_val)

                if res_val < max_relative_residual:
                    converged_this_step = True
                    # Quan trọng: Lưu lại nghiệm tốt nhất để làm móng cho bước sau
                    last_step_checkpoint = current_magnetic_potential.copy()
                    break
                j += 1
            
            # --- Xử lý Backtrack Tầng 2 sau khi vòng lặp j kết thúc ---
            if not converged_this_step:
                if l2_retry < l2_limit:
                    l2_retry += 1
                    initial_step_damping *= 0.5 # Giảm damping khởi đầu đi một nửa
                    if debug:
                        print(f"   {YELLOW}[!!] BACKTRACK TẦNG 2: Không hội tụ Step {i+1}. Thử lại với Damping khởi đầu = {initial_step_damping:.4f}{RESET}")
                else:
                    if debug:
                        print(f"   {RED}[!!!] THẤT BẠI HOÀN TOÀN tại Step {i+1}. Tiếp tục với sai số hiện tại.{RESET}")
                    # Nếu quá giới hạn retry L2, vẫn coi như xong bước này để không bị lặp vô hạn
                    last_step_checkpoint = current_magnetic_potential.copy()
                    break
        
        i += 1 # Chuyển sang bước tải tiếp theo

    reluctance_network.add_elements_lite()

    if debug and residual_history:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        if len(residual_history) > 2:
            residual_history[0] = residual_history[1] * 1.5
            
        ax.plot(residual_history, color='teal', marker='o', markersize=3, label='Equation Residual')
        for idx in load_step_indices:
            ax.axvline(x=idx, color='red', linestyle='--', alpha=0.3)
            
        ax.set_yscale('log')
        ax.set_xlabel("Cumulative Iterations")
        ax.set_ylabel("Relative Residual (||GP-J||/||J||)")
        ax.set_title("Robust Convergence History with Level 2 Backtracking")
        ax.axhline(y=max_relative_residual, color='orange', linestyle=':', label='Target')
        ax.grid(True, which="both", alpha=0.2)
        ax.legend()
        plt.tight_layout()
        plt.show()
        if hasattr(reluctance_network, 'show'): reluctance_network.show()