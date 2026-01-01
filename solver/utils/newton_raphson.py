import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def function_nonlinear_load(load_step, order=2):
    x = np.linspace(0, 1, load_step + 1)[1:]
    return (1 - np.exp(-order * x)) / (1 - np.exp(-order))

def newton_raphson_iteration(reluctance_network, 
                             max_iteration=30, 
                             max_relative_residual=1e-3, 
                             load_step=5, 
                             debug=True):
    """
    Giải bài toán từ trường bằng phương pháp Newton-Raphson.
    Sử dụng ma trận Jacobian (Ja) để cập nhật bước lặp: x_{k+1} = x_k - Ja^-1 * R(x_k)
    """

    # 1. Khởi tạo
    reluctance_network.set_reluctance_at_zero()
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()
    last_step_checkpoint = current_magnetic_potential.copy()
    
    load_queue = list(function_nonlinear_load(load_step, order=2))
    residual_history = []
    load_step_indices = []
    last_converged_load = 0.0

    # Màu sắc console
    GREEN, RED, YELLOW, CYAN, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[0m"

    while load_queue:
        current_load = load_queue.pop(0)
        # Bắt đầu mỗi load step từ kết quả hội tụ của bước trước
        current_magnetic_potential = last_step_checkpoint.copy()
        converged_this_step = False
        
        for j in range(max_iteration):
            if j == 0: load_step_indices.append(len(residual_history))

            # --- BƯỚC 1: Cập nhật mạng và lấy các ma trận ---
            reluctance_network.magnetic_potential.data = current_magnetic_potential
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            
            # Gọi hàm tạo phương trình (Lấy cả G, J và Ja)
            comp = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
            G, J, Ja = comp.G, comp.J, comp.Ja
            
            # --- BƯỚC 2: Tính Residual (Phần dư) R(x) = G*x - J ---
            # x_k hiện tại
            x_k = current_magnetic_potential.flatten(order='F')[:-1] # Bỏ nút tham chiếu cuối
            
            # Residual: f(x) = G*x - J
            residual_vector = G.dot(x_k) - J
            res_norm = np.linalg.norm(residual_vector)
            norm_J = np.linalg.norm(J) + 1e-12
            rel_res = res_norm / norm_J
            
            residual_history.append(rel_res)

            if debug:
                print(f"Load {current_load:.4f}, Iter {j+1}: Rel Res = {rel_res*100:.6f}%")

            # --- BƯỚC 3: Kiểm tra hội tụ ---
            if rel_res < max_relative_residual:
                converged_this_step = True
                last_step_checkpoint = current_magnetic_potential.copy()
                last_converged_load = current_load
                print(f"{GREEN}  [v] Load {current_load:.4f} Converged.{RESET}")
                break

            # --- BƯỚC 4: Giải hệ Newton: Ja * delta_x = -residual_vector ---
            try:
                delta_x = spsolve(Ja, -residual_vector)
            except Exception as e:
                print(f"{RED}  [!] Matrix Solver Error: {e}{RESET}")
                break

            # --- BƯỚC 5: Cập nhật nghiệm ---
            # Thêm 0.0 cho nút tham chiếu nếu cần (tùy cấu trúc mạng của bạn)
            delta_x_full = np.append(delta_x, 0.0) 
            x_next_flat = current_magnetic_potential.flatten(order='F') + delta_x_full
            current_magnetic_potential = x_next_flat.reshape(magnetic_potential_shape, order='F')

        # Xử lý nếu không hội tụ (Sub-stepping)
        if not converged_this_step:
            mid_load = (last_converged_load + current_load) / 2
            if abs(current_load - last_converged_load) > 1e-5:
                load_queue.insert(0, current_load)
                load_queue.insert(0, mid_load)
                if debug:
                    print(f"   {YELLOW}[!!] Newton Diverged. Splitting load step to {mid_load:.4f}{RESET}")
            else:
                print(f"   {RED}[!!!] FATAL: Cannot converge at load {current_load:.4f}{RESET}")
                break

    # Cập nhật kết quả cuối cùng
    reluctance_network.add_elements_lite()

    # Vẽ biểu đồ
    if debug and residual_history:
        plt.figure(figsize=(8, 5))
        plt.semilogy(residual_history, color='crimson', lw=1.5, label='Newton Residual')
        for idx in load_step_indices:
            plt.axvline(x=idx, color='k', linestyle='--', alpha=0.2)
        plt.title("Newton-Raphson Convergence History")
        plt.xlabel("Total Iterations")
        plt.ylabel("Relative Residual")
        plt.grid(True, which="both", alpha=0.3)
        plt.legend()
        plt.show()

    return last_step_checkpoint