import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
import time

def advanced_solver(reluctance_network, 
                  initial_damping_factor=0.1,  # Hệ số giảm chấn nghiệm (Alpha)
                  initial_material_relax=0.1,  # Hệ số thư giãn vật liệu (Eta)
                  max_iteration=300, 
                  max_relative_residual=0.05, 
                  debug=True):
    """
    ADVANC SOLVER
    Thuật toán điểm bất động (Fixed-Point) với cơ chế điều khiển thích nghi (Adaptive Control).
    """
    
    G_c, M_c, Y_c, C_c, R_c, RESET = "\033[92m", "\033[95m", "\033[93m", "\033[96m", "\033[91m", "\033[0m"

    print(f"\n{Y_c}{'='*100}")
    print(f" ADVANC SOLVER | LOAD: 1.0 | INIT DAMPING: {initial_damping_factor} | INIT RELAX: {initial_material_relax}")
    print(f"{'='*100}{RESET}")

    reluctance_network.set_reluctance_at_zero()
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    current_pot = reluctance_network.magnetic_potential.data.copy()
    
    # --- KHỞI TẠO BIẾN ĐIỀU KHIỂN ---
    target_load = 1.0
    
    # Biến chạy (Current)
    curr_damping = initial_damping_factor
    curr_relax = initial_material_relax
    
    prev_true_phi = 1.0 
    start_time = time.time()

    if debug:
        print(f"{M_c}{'Iter':>5} | {'Apparent':>12} | {'TRUE RES':>15} | {'Damping':>8} | {'Status'}{RESET}")

    j = 0
    while j < max_iteration:
        j += 1
        
        # 1. BACKUP (Lưu trạng thái cũ để phòng hờ)
        backup_pot = current_pot.copy()
        
        # 2. TÍNH HƯỚNG ĐI (Direction Step)
        # Cập nhật vật liệu với hệ số thư giãn (Relaxation)
        reluctance_network.update_reluctance_network(
            magnetic_potential=reluctance_network.magnetic_potential,
            material_relaxation_factor=curr_relax
        )
        comp_damped = reluctance_network.create_magnetic_potential_equation(load_factor=target_load)
        
        # Tính sai số ảo (Apparent) để tham khảo
        phi_apparent = np.linalg.norm(comp_damped.J - comp_damped.G.dot(backup_pot.flatten(order='F')[:-1])) / (np.linalg.norm(comp_damped.J) + 1e-12)

        try:
            p_target_active = spsolve(comp_damped.G, comp_damped.J)
        except:
            print(f" {R_c}Matrix Singular! Reducing parameters...{RESET}")
            curr_damping *= 0.5
            curr_relax *= 0.8
            continue 

        # 3. CẬP NHẬT NGHIỆM (Update Step)
        p_active = backup_pot.flatten(order='F')[:-1]
        d_vec = p_target_active - p_active
        
        # Áp dụng Damping Factor vào bước nhảy
        p_new_active = p_active + curr_damping * d_vec
        
        trial_pot = np.append(p_new_active, 0.0).reshape(mag_pot_shape, order='F')
        reluctance_network.magnetic_potential.data = trial_pot

        # 4. KIỂM CHỨNG (Validation Step)
        # Ép Relax = 1.0 để tính sai số thực tế
        reluctance_network.update_reluctance_network(
            magnetic_potential=reluctance_network.magnetic_potential,
            material_relaxation_factor=1.0 
        )
        comp_true = reluctance_network.create_magnetic_potential_equation(load_factor=target_load)
        phi_true = np.linalg.norm(comp_true.J - comp_true.G.dot(p_new_active)) / (np.linalg.norm(comp_true.J) + 1e-12)

        # 5. ĐIỀU KHIỂN THÍCH NGHI (Adaptive Logic)
        if phi_true < prev_true_phi:
            # --- ACCEPT ---
            current_pot = trial_pot.copy()
            status = f"{G_c}ACCEPTED{RESET}"
            prev_true_phi = phi_true
            
            # Tăng tốc nhẹ nếu đang ổn định (Max 0.5)
            if j > 5 and curr_damping < 0.5: 
                curr_damping *= 1.05
            
        else:
            # --- REJECT ---
            reluctance_network.magnetic_potential.data = backup_pot # Khôi phục
            status = f"{R_c}REJECTED{RESET}"
            
            # Giảm tốc độ (Đạp phanh)
            curr_damping *= 0.5
            curr_relax *= 0.8
            
            # Giới hạn an toàn tối thiểu
            if curr_damping < 1e-4: curr_damping = 1e-4
            if curr_relax < 0.01: curr_relax = 0.01

        if debug:
            print(f"  {j:03d} | {phi_apparent*100:10.4f}% | {phi_true*100:13.6f}% | {curr_damping:.4f} | {status}")

        # --- KIỂM TRA ĐIỀU KIỆN DỪNG ---
        if phi_true < max_relative_residual:
            print(f"\n{G_c}>>> HỘI TỤ HOÀN TOÀN! (Time: {time.time() - start_time:.2f}s){RESET}")
            reluctance_network.add_elements_lite()
            return 

    print(f"\n{Y_c}>>> MAX ITERATION REACHED. Finalizing...{RESET}")
    reluctance_network.add_elements_lite()