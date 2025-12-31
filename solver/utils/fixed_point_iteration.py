import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def function_nonlinear_load(load_step, order=2):
    x = np.linspace(0, 1, load_step + 1)[1:]
    return (1 - np.exp(-order * x)) / (1 - np.exp(-order))

def fix_point_iteration(reluctance_network, 
                        max_iteration=150, 
                        max_relative_residual=1e-5, 
                        load_step=10, 
                        adaptive_damping_factor=(1.0, 0.1),
                        debug=True):

    reluctance_network.set_reluctance_at_zero()
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_p = reluctance_network.magnetic_potential.data.copy()
    last_stable_p = current_p.copy()
    
    # Khởi tạo danh sách các mức tải (Load queue)
    load_queue = list(function_nonlinear_load(load_step, order=2))
    
    # Thông số Pseudo-transient Continuation (Psi-tc) từ tài liệu [cite: 4, 19]
    delta_init = 0.5 
    delta_min = 1e-6
    delta_max = 1.0 # Giới hạn tối đa để tiệm cận Newton [cite: 21, 147]
    delta = delta_init
    
    residual_history = []
    load_step_indices = []
    last_converged_load = 0.0

    GREEN, RED, WHITE, YELLOW, CYAN, RESET = "\033[92m", "\033[91m", "\033[97m", "\033[93m", "\033[96m", "\033[0m"

    while load_queue:
        current_load = load_queue.pop(0)
        current_p = last_stable_p.copy()
        converged_this_step = False
        
        j = 0
        while j < max_iteration:
            # Đánh dấu điểm bắt đầu bước tải mới trên đồ thị
            if j == 0: load_step_indices.append(len(residual_history))

            # Lập phương trình trạng thái ổn định F(x)
            reluctance_network.magnetic_potential.data = current_p.reshape(magnetic_potential_shape, order='F')
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            comp = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
            
            G, J = comp.G, comp.J
            norm_J = np.linalg.norm(J) + 1e-12
            
            # Giải hệ tuyến tính
            p_sol = spsolve(G, J)
            g_x = np.append(p_sol, 0.0)
            x_k = current_p.flatten(order='F')
            f_k = g_x - x_k # Vector sai số (Update vector)
            
            # Tính Residual phi tuyến thực tế để cập nhật SER [cite: 76, 318]
            reluctance_network.magnetic_potential.data = g_x.reshape(magnetic_potential_shape, order='F')
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            comp_new = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
            res_val = np.linalg.norm(comp_new.G.dot(p_sol) - J) / norm_J

            if debug:
                color = WHITE if j == 0 else (GREEN if (len(residual_history) > 0 and res_val < residual_history[-1]) else RED)
                print(f"{color}Load {current_load:.4f}, Iter {j+1}: delta = {delta:.4f}, Res = {res_val*100:.4f}%{RESET}")

            # --- Logic Thất bại sớm & Tối ưu hóa Backtrack ---
            if j > 0 and len(residual_history) > 0:
                if res_val > residual_history[-1] * 1.5:
                    if debug: print(f"   {RED}[!] Divergence! Kích hoạt Backtrack Tầng 2...{RESET}")
                    break 

                # Công thức SER: Tăng delta khi hội tụ tốt 
                ratio = residual_history[-1] / (res_val + 1e-20)
                delta = np.clip(delta * ratio, delta_min, delta_max)

            residual_history.append(res_val)

            if res_val < max_relative_residual:
                converged_this_step = True
                last_stable_p = g_x.reshape(magnetic_potential_shape, order='F')
                last_converged_load = current_load
                # Reset delta mạnh cho bước tải tiếp theo khi đã hội tụ [cite: 21]
                delta = delta_max 
                break

            # Cập nhật nghiệm theo bước thời gian giả delta [cite: 48, 125]
            current_p = (x_k + delta * f_k).reshape(magnetic_potential_shape, order='F')
            j += 1
            
        # --- Backtracking Tầng 2: Chia tải & Giảm 1/2 damping ngay lập tức ---
        if not converged_this_step:
            mid_load = (last_converged_load + current_load) / 2
            if abs(current_load - last_converged_load) > 1e-5:
                load_queue.insert(0, current_load)
                load_queue.insert(0, mid_load)
                # Giảm damping còn 1 nửa lập tức để đảm bảo an toàn cho bước trung gian
                delta = delta_init * 0.5 
                if debug:
                    print(f"   {YELLOW}[!!] L2 BACKTRACK: Chèn bước {mid_load:.4f}, Damping -> {delta:.4f}{RESET}")
            else:
                if debug: print(f"   {RED}[!!!] THẤT BẠI: Không thể hội tụ tại mức tải {current_load:.4f}{RESET}")
                break

    reluctance_network.add_elements_lite()

    # --- Phần vẽ đồ thị lịch sử hội tụ ---
    if debug and residual_history:
        fig, ax = plt.subplots(figsize=(12, 7), dpi=100)
        
        # Vẽ đường sai số dư
        ax.plot(residual_history, color='teal', marker='o', markersize=3, 
                linewidth=1, label='Equation Residual (Normalized)')
        
        # Vẽ các vạch đỏ đánh dấu Load Steps
        for idx in load_step_indices:
            ax.axvline(x=idx, color='red', linestyle='--', alpha=0.3)
            
        # Đường mục tiêu (Target)
        ax.axhline(y=max_relative_residual, color='orange', linestyle=':', 
                   linewidth=2, label=f'Target ({max_relative_residual})')
        
        # Định dạng đồ thị theo thang Log
        ax.set_yscale('log')
        ax.set_xlabel("Cumulative Iterations (Total steps across all loads)")
        ax.set_ylabel("Relative Residual ||G*P - J|| / ||J||")
        ax.set_title("Robust Convergence via Pseudo-transient Continuation ($\Psi tc$) & SER")
        
        ax.grid(True, which="both", ls="-", alpha=0.15)
        ax.legend(loc='upper right')
        
        plt.tight_layout()
        plt.show()