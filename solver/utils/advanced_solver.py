import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
import time
import matplotlib.pyplot as plt

def advanced_solver(reluctance_network, 
                    material_relax=0.5,   
                    node_damping=0.05,      
                    max_iteration=200,    
                    max_relative_residual=5e-3, 
                    debug=True):
    
    # Mã màu
    G_c, Y_c, R_c, C_c, B_c, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[96m", "\033[94m", "\033[0m"

    if debug: 
        print(f"\n{Y_c}{'='*120}")
        print(f" STRICT MONOTONIC SOLVER (Stop on Increase)")
        print(f" Relax: {material_relax} | Damping: {node_damping}")
        print(f"{'='*120}{RESET}")
        print(f"{B_c}{'Iter':>4} | {'Curr Res':>12} | {'Best Res':>12} | {'Step Norm':>10} | {'Status'}{RESET}")
        print(f"{'-'*120}")
    
    best_residual_history = []
    
    # --- KHỞI TẠO ---
    reluctance_network.set_reluctance_at_zero()
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    
    best_pot_data = reluctance_network.magnetic_potential.data.copy()
    best_phi = float('inf') 
    
    start_time = time.time()

    for j in range(1, max_iteration + 1):
        # 1. PREDICTOR
        reluctance_network.update_reluctance_network(
            magnetic_potential=reluctance_network.magnetic_potential,
            material_relaxation_factor=material_relax, 
            delta_mu_max=-1 
        )
        
        comp = reluctance_network.create_magnetic_potential_equation(load_factor=1.0)
        p_current_active = reluctance_network.magnetic_potential.data.flatten(order='F')[:-1]

        # 2. SOLVE
        try:
            p_target_active = spsolve(comp.G, comp.J)
        except Exception as e:
            if debug: print(f"{R_c}!!! SOLVER FAILED: {e}{RESET}")
            break

        # 3. UPDATE
        raw_step = p_target_active - p_current_active
        raw_step_norm = np.linalg.norm(raw_step) / (np.linalg.norm(p_current_active) + 1e-12)
        
        p_new_active = p_current_active + node_damping * raw_step
        reluctance_network.magnetic_potential.data = np.append(p_new_active, 0.0).reshape(mag_pot_shape, order='F')

        # 4. VALIDATOR
        reluctance_network.update_reluctance_network(
            magnetic_potential=reluctance_network.magnetic_potential,
            material_relaxation_factor=1.0, 
            delta_mu_max=-1
        )
        v_comp = reluctance_network.create_magnetic_potential_equation(load_factor=1.0)
        
        res_vector = v_comp.J - v_comp.G.dot(p_new_active)
        phi_true = np.linalg.norm(res_vector) / (np.linalg.norm(v_comp.J) + 1e-12)

        # 5. LOGIC DỪNG SỚM (STOP ON INCREASE)
        status_msg = ""
        
        if phi_true < best_phi:
            # === CÓ CẢI THIỆN ===
            improvement = best_phi - phi_true
            imp_str = "INIT" if best_phi == float('inf') else f"-{improvement:.2e}"
            
            best_phi = phi_true
            best_pot_data = reluctance_network.magnetic_potential.data.copy()
            status_msg = f"{G_c}NEW BEST ({imp_str}){RESET}"
            
            best_residual_history.append(phi_true)
            
            if debug:
                print(f" {j:03d} | {phi_true*100:10.6f}% | {best_phi*100:10.6f}% | {raw_step_norm:.2e} | {status_msg}")

        else:
            # === SAI SỐ TĂNG -> DỪNG LUÔN ===
            diff = phi_true - best_phi
            status_msg = f"{R_c}WORSENED (+{diff:.2e}){RESET}"
            
            best_residual_history.append(phi_true) # Lưu nốt điểm này để vẽ đồ thị thấy điểm gãy
            
            if debug:
                print(f" {j:03d} | {phi_true*100:10.6f}% | {best_phi*100:10.6f}% | {raw_step_norm:.2e} | {status_msg}")
                print(f"\n{Y_c}>>> STOPPED EARLY: Residual increased. Reverting to best result.{RESET}")
            break # <--- LỆNH DỪNG VÒNG LẶP

        # Điều kiện hội tụ
        if best_phi < max_relative_residual:
            if debug: print(f"\n{G_c}>>> SUCCESS: Converged at {best_phi*100:.6f}%{RESET}")
            break

    # KẾT THÚC: Khôi phục nghiệm tốt nhất
    reluctance_network.magnetic_potential.data = best_pot_data
    reluctance_network.add_elements_lite()
    
    """
    if debug:
        print(f"Total Time: {time.time() - start_time:.2f}s")
        if len(best_residual_history) > 0:
            try:
                plt.figure(figsize=(10, 6))
                plt.plot(best_residual_history, marker='o', markersize=4, color='b', linewidth=1)
                # Đánh dấu điểm cuối cùng bị fail (nếu có) bằng màu đỏ
                if len(best_residual_history) > 1 and best_residual_history[-1] > best_residual_history[-2]:
                    plt.plot(len(best_residual_history)-1, best_residual_history[-1], 'rx', markersize=10, label='Stop Point')
                
                plt.yscale('log')
                plt.title('Convergence (Stop on Increase)')
                plt.xlabel('Iteration')
                plt.ylabel('Residual (Log)')
                plt.grid(True, which="both", alpha=0.5)
                plt.legend()
                plt.show()
            except: pass
    """

    return best_phi, best_residual_history