import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def function_nonlinear_load(load_step, order=2):
    x = np.linspace(0, 1, load_step + 1)[1:]
    return (1 - np.exp(-order * x)) / (1 - np.exp(-order))

def newton_raphson_iteration(reluctance_network, 
                             max_iteration=30, 
                             max_relative_residual=5e-2, 
                             load_step=10, 
                             debug=True):
    
    # --- KHỞI TẠO HỆ THỐNG ---
    reluctance_network.set_reluctance_at_zero()
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()
    last_step_checkpoint = current_magnetic_potential.copy()
    
    load_queue = list(function_nonlinear_load(load_step, order=2))
    residual_history = []
    load_step_indices = []
    last_converged_load = 0.0

    GREEN, RED, YELLOW, CYAN, WHITE, BOLD, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[97m", "\033[1m", "\033[0m"

    if debug:
        print(f"{BOLD}{CYAN}>>> BẮT ĐẦU DAMPED NEWTON-RAPHSON SOLVER <<<{RESET}")
        print("-" * 60)

    while load_queue:
        current_load = load_queue.pop(0)
        current_magnetic_potential = last_step_checkpoint.copy()
        converged_this_step = False
        
        # Khởi tạo damping ban đầu cho mỗi bước tải
        current_damping = 1.0 
        
        if debug:
            print(f"{BOLD}Mức tải: {current_load:.4f}{RESET}")

        for iteration in range(max_iteration):
            if iteration == 0: 
                load_step_indices.append(len(residual_history))

            # --- BƯỚC 1: CẬP NHẬT MẠNG ---
            reluctance_network.magnetic_potential.data = current_magnetic_potential
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            
            comp = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
            G, J, Ja = comp.G, comp.J, comp.Ja
            
            # --- BƯỚC 2: TÍNH SAI SỐ ---
            x_k = current_magnetic_potential.flatten(order='F')[:-1] 
            residual_vector = G.dot(x_k) - J
            relative_residual = np.linalg.norm(residual_vector) / (np.linalg.norm(J) + 1e-12)
            
            residual_history.append(relative_residual)

            # --- CHIẾN LƯỢC ADAPTIVE DAMPING (CẬP NHẬT PHANH) ---
            if iteration > 0:
                # Nếu sai số tăng so với bước trước -> NR đang vọt lố (Overshooting)
                if relative_residual > residual_history[-2]:
                    current_damping *= 0.5 # Siết phanh mạnh hơn
                    if debug:
                        print(f"    {YELLOW}[CẢNH BÁO] Sai số tăng! Giảm Damping xuống: {current_damping}{RESET}")
                # Nếu sai số giảm rất sâu -> Có thể nới phanh từ từ để tăng tốc
                elif relative_residual < 0.01:
                    current_damping = min(1.0, current_damping * 1.2)

            if debug:
                color = GREEN if (iteration > 0 and relative_residual < residual_history[-2]) else WHITE
                print(f"  {color}Lặp {iteration + 1:2d}: Res = {relative_residual * 100:.4f}% | Damping = {current_damping:.2f}{RESET}")

            # --- BƯỚC 3: KIỂM TRA HỘI TỤ ---
            if relative_residual < max_relative_residual:
                converged_this_step = True
                last_step_checkpoint = current_magnetic_potential.copy()
                last_converged_load = current_load
                if debug:
                    print(f"  {GREEN}[v] Hội tụ tại {current_load:.4f}{RESET}\n")
                break

            # --- BƯỚC 4: GIẢI HỆ NEWTON ---
            try:
                delta_x = spsolve(Ja, -residual_vector)
            except:
                break

            # --- BƯỚC 5: CẬP NHẬT NGHIỆM VỚI DAMPING ---
            delta_x_full = np.append(delta_x, 0.0) 
            # Nghiệm mới = Nghiệm cũ + Damping * Bước nhảy Newton
            x_next_flat = current_magnetic_potential.flatten(order='F') + current_damping * delta_x_full
            current_magnetic_potential = x_next_flat.reshape(magnetic_potential_shape, order='F')

        if not converged_this_step:
            mid_load = (last_converged_load + current_load) / 2
            if abs(current_load - last_converged_load) > 1e-5:
                load_queue.insert(0, current_load)
                load_queue.insert(0, mid_load)
                if debug: print(f"  {YELLOW}>>> Chia nhỏ bước tải -> {mid_load:.4f}{RESET}\n")
            else:
                break

    reluctance_network.add_elements_lite()
    return last_step_checkpoint