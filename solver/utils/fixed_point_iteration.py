import numpy as np
from scipy.sparse.linalg import spsolve

def fix_point_iteration(reluctance_network, 
                        max_iteration=10, 
                        debug=True):
    
    # Khởi tạo từ trở ban đầu
    reluctance_network.set_reluctance_at_zero()
    
    current_phi = reluctance_network.loop_flux.data.copy()

    # damping mặc định
    damping = 0.1

    if debug:
        print(f"--- Starting Minimal Fixpoint Iteration ({max_iteration} steps) ---")
        print(f"    Damping factor = {damping}")

    for j in range(max_iteration):

        # (1) Gán phi hiện tại
        reluctance_network.loop_flux.data = current_phi

        # (2) Cập nhật từ trở theo phi (phi tuyến)
        reluctance_network.update_reluctance_network(
            loop_flux=reluctance_network.loop_flux
        )

        # (3) Lập hệ tuyến tính
        comp = reluctance_network.create_loop_flux_equation(
            load_factor=1.0,
            debug=False
        )
        R = comp.R
        F = comp.F

        # (4) Giải hệ tuyến tính
        phi_new = spsolve(R, F)

        # (5) Residual phi tuyến đúng
        norm_F = np.linalg.norm(F) + 1e-12
        residual = np.linalg.norm(R.dot(current_phi) - F) / norm_F

        # ===== DAMPING (UNDER-RELAXATION) =====
        current_phi = (
            damping * phi_new
            + (1.0 - damping) * current_phi
        )
        # =====================================

        if debug:
            print(f"Step {j+1}/{max_iteration}: Residual = {residual*100:.6f}%")

    # Ghi nghiệm cuối
    reluctance_network.loop_flux.data = current_phi
    reluctance_network.add_elements_lite()
    
    if debug:
        print("--- Iteration Finished ---")
        
    return reluctance_network
