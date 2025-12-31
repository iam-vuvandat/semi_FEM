import numpy as np
import matplotlib.pyplot as plt
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

def newton_raphson(reluctance_network, 
                    adaptive_damping_factor=None,
                    max_iteration=150, 
                    max_relative_residual=1e-5, 
                    load_step=10, 
                    debug=True):

    reluctance_network.set_reluctance_at_zero()
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_p = reluctance_network.magnetic_potential.data.copy()
    last_stable_p = current_p.copy()
    
    # Khởi tạo danh sách các mức tải
    load_queue = list(function_nonlinear_load(load_step, order=2))
    
    # Thông số Psi-tc: Duy trì tính ổn định toàn cục
    delta_init = 0.5 
    delta_min = 1e-6
    delta_max = 1.0 
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
            if j == 0: load_step_indices.append(len(residual_history))

            # 1. Cập nhật trạng thái mạng từ trở
            reluctance_network.magnetic_potential.data = current_p.reshape(magnetic_potential_shape, order='F')
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            
            # 2. Lấy hệ phương trình với Jacobian Số trị (Ja_numeric)
            # Chúng ta kích hoạt compute_numeric=True để lấy đạo hàm chính xác từ sai phân hữu hạn
            comp = reluctance_network.create_magnetic_potential_equation(
                load_factor=current_load, 
                debug=False
            )
            
            G, J_source, Ja = comp.G, comp.J, comp.Ja_numeric
            
            # 3. Tính Vector dư Residual: F(P) = G*P - J_source
            p_flat = current_p.flatten(order='F')[:-1] 
            residual_vector = G.dot(p_flat) - J_source
            
            norm_res = np.linalg.norm(residual_vector)
            norm_J = np.linalg.norm(J_source) + 1e-12
            res_val = norm_res / norm_J

            if debug:
                color = WHITE if j == 0 else (GREEN if (len(residual_history) > 0 and res_val < residual_history[-1]) else RED)
                print(f"{color}Load {current_load:.4f}, Iter {j+1}: delta = {delta:.4f}, Res = {res_val*100:.4f}%{RESET}")

            # --- KIỂM TRA HỘI TỤ ---
            if res_val < max_relative_residual:
                converged_this_step = True
                last_stable_p = current_p.copy()
                last_converged_load = current_load
                delta = delta_max # Reset delta cho bước tải kế tiếp
                break

            # --- CHIẾN THUẬT SER (Switched Evolution Relaxation) ---
            if j > 0 and res_val > residual_history[-1] * 1.02: # Phanh gấp nếu sai số tăng
                delta *= 0.5
                if debug: print(f"   {YELLOW}[!] Divergence Risk: delta -> {delta:.4f}{RESET}")
                if delta < delta_min: break
            else:
                if j > 0:
                    # Tăng tốc độ hội tụ khi sai số giảm ổn định
                    ratio = residual_history[-1] / (res_val + 1e-20)
                    delta = np.clip(delta * ratio, delta_min, delta_max)

            residual_history.append(res_val)

            # 4. GIẢI HỆ NEWTON: (Ja_numeric + (1/delta)*I) * dP = -F(P)
            matrix_size = G.shape[0]
            # Thành phần ổn định hóa (Diagonal Stabilization) giúp Newton hội tụ toàn cục
            stabilization = sp.eye(matrix_size) * (1.0 / (delta + 1e-12))
            
            try:
                # Tìm bước nhảy dP bằng ma trận Jacobian số trị đáng tin cậy
                delta_p = spsolve(Ja + stabilization, -residual_vector)
            except Exception as e:
                if debug: print(f"   {RED}[!] Solver Error: {e}. Breaking...{RESET}")
                break

            # 5. CẬP NHẬT NGHIỆM
            p_flat += delta_p
            current_p = np.append(p_flat, 0.0).reshape(magnetic_potential_shape, order='F')
            j += 1
            
        # --- QUẢN LÝ BACKTRACKING TẢI ---
        if not converged_this_step:
            mid_load = (last_converged_load + current_load) / 2
            if abs(current_load - last_converged_load) > 1e-5:
                load_queue.insert(0, current_load)
                load_queue.insert(0, mid_load)
                delta = delta_init
                if debug: print(f"   {CYAN}>>> Backtrack: Chèn bước tải trung gian {mid_load:.4f}{RESET}")
            else:
                if debug: print(f"   {RED}[!!!] Failed to converge at load {current_load:.4f}{RESET}")
                break

    reluctance_network.add_elements_lite()
    return current_p

def function_nonlinear_load(load_step, order=2):
    x = np.linspace(0, 1, load_step + 1)[1:]
    return (1 - np.exp(-order * x)) / (1 - np.exp(-order))