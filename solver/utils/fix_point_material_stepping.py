import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def fix_point_material_stepping(reluctance_network, 
                                 max_iteration=40, 
                                 max_relative_residual=1e-3, 
                                 debug=True):
    
    # 1. Khởi tạo và Backup trạng thái ban đầu
    # Đảm bảo material_database đã chạy smooth_BH_curve
    reluctance_network.set_reluctance_at_zero()
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    current_pot = reluctance_network.magnetic_potential.data.copy()
    
    # Danh sách Loadstep vật liệu (từ cứng đến thực tế)
    # 0.1: Vật liệu dẫn từ kém (tuyến tính hơn) -> 1.0: Vật liệu thực tế
    material_queue = [0.1, 0.3, 0.6, 0.8, 1.0]
    
    history_residual = []
    history_load_markers = []
    
    G_c, R_c, Y_c, C_c, RESET = "\033[92m", "\033[91m", "\033[93m", "\033[96m", "\033[0m"

    if debug:
        print(f"\n{C_c}{'='*80}")
        print(f" THUẬT TOÁN: MATERIAL LOAD-STEPPING (λm)")
        print(f"{'='*80}{RESET}")

    for m_factor in material_queue:
        if debug:
            print(f"\n{Y_c}>>> [MATERIAL STEP] Hệ số tải vật liệu λm = {m_factor:.2f}{RESET}")
            print(f"{'-'*60}")
        
        # Cập nhật đường cong B-H của vật liệu sắt theo λm
        reluctance_network.material_database.step_permeability(load_factor=m_factor)
        
        history_load_markers.append(len(history_residual))
        phi_old = float('inf')

        for j in range(max_iteration):
            # Cập nhật ma trận độ từ trở dựa trên thế từ hiện tại
            reluctance_network.magnetic_potential.data = current_pot
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            
            # Tạo hệ phương trình với nguồn CỐ ĐỊNH 100% (load_factor=1.0)
            comp = reluctance_network.create_magnetic_potential_equation(load_factor=1.0, debug=False)
            
            p_active = current_pot.flatten(order='F')[:-1] 
            norm_j = np.linalg.norm(comp.J) + 1e-12
            res_current = np.linalg.norm(comp.G.dot(p_active) - comp.J) / norm_j
            
            if debug: print(f"  Iter {j+1:2d} | Residual: {res_current*100:10.6f}%")

            # Kiểm tra hội tụ của Loadstep vật liệu hiện tại
            if res_current < max_relative_residual:
                if debug: print(f"  {G_c}✓ Bước λm = {m_factor} đạt hội tụ.{RESET}")
                break

            # Giải tìm hướng nghiệm
            p_sol_active = spsolve(comp.G, comp.J)
            p_sol_full = np.append(p_sol_active, 0.0).reshape(mag_pot_shape, order='F')
            direction = p_sol_full - current_pot

            # --- DUAL-PHASE LINE SEARCH (Tối ưu hóa bước nhảy) ---
            def evaluate_alpha(a):
                p_t = current_pot + a * direction
                reluctance_network.magnetic_potential.data = p_t
                reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                comp_t = reluctance_network.create_magnetic_potential_equation(load_factor=1.0, debug=False)
                res = np.linalg.norm(comp_t.G.dot(p_t.flatten(order='F')[:-1]) - comp_t.J) / norm_j
                return res, p_t

            # Quét thô (Coarse Scan)
            alphas = np.linspace(0.1, 1.0, 8)
            best_a = 0.1
            best_res, best_pot = evaluate_alpha(best_a)

            for a in alphas[1:]:
                r, p = evaluate_alpha(a)
                if r < best_res:
                    best_res, best_pot, best_a = r, p, a
            
            # Cập nhật nghiệm sau Line Search
            current_pot = best_pot.copy()
            history_residual.append(best_res)
            
            if debug:
                print(f"    - Alpha selected: {best_a:.2f} | New Residual: {best_res*100:.6f}%")

            # Chống đứng hình (Stagnation)
            if abs(phi_old - best_res) < 1e-9:
                if debug: print(f"  {R_c}⚠ Stagnation. Chuyển bước tiếp theo.{RESET}")
                break
            phi_old = best_res

    # Kết thúc: Khôi phục vật liệu về thực tế (đề phòng) và lưu nghiệm
    reluctance_network.material_database.continuous_permeability()
    reluctance_network.magnetic_potential.data = current_pot
    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
    reluctance_network.add_elements_lite()

    # Vẽ lịch sử hội tụ
    if debug and history_residual:
        plt.figure(figsize=(10, 5))
        plt.semilogy(history_residual, 'r-x', label='Material Stepping Residual')
        for marker in history_load_markers:
            plt.axvline(x=marker, color='k', linestyle='--', alpha=0.3)
        plt.title('Convergence History: Material Load-Stepping')
        plt.xlabel('Iterations')
        plt.ylabel('Relative Residual')
        plt.grid(True, which="both", alpha=0.2)
        plt.legend()
        plt.show()

    return reluctance_network