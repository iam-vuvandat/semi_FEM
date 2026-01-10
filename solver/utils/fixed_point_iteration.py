import numpy as np
from scipy.sparse.linalg import spsolve

def fix_point_iteration(reluctance_network, 
                                         max_iteration=10, 
                                         debug=True):
    
    reluctance_network.set_reluctance_at_zero()
    
    current_phi = reluctance_network.loop_flux.data.copy()

    GREEN, RED, RESET = "\033[92m", "\033[91m", "\033[0m"

    if debug:
        print(f"--- Starting Minimal Fixpoint Iteration ({max_iteration} steps) ---")

    for j in range(max_iteration):
        # 2. Cập nhật độ từ dẫn/từ trở dựa trên từ thông hiện tại (xử lý phi tuyến)
        reluctance_network.loop_flux.data = current_phi
        reluctance_network.update_reluctance_network(loop_flux=reluctance_network.loop_flux)

        # 3. Lập hệ phương trình vòng: R(phi) * phi_new = F
        # load_factor cố định bằng 1.0 vì không dùng chiến thuật chia bước tải
        comp = reluctance_network.create_loop_flux_equation(load_factor=1.0, debug=False)
        R = comp.R
        F = comp.F

        # 4. Giải hệ phương trình tuyến tính
        # Sử dụng spsolve để tìm nghiệm phi mới
        phi_new = spsolve(R, F)

        # 5. Tính sai số (Residual) để theo dõi
        norm_F = np.linalg.norm(F) + 1e-12
        residual = np.linalg.norm(R.dot(phi_new) - F) / norm_F
        
        # 6. Cập nhật biến cho bước lặp sau
        current_phi = phi_new

        if debug:
            print(f"Step {j+1}/{max_iteration}: Residual = {residual*100:.4f}%")

    # Cập nhật kết quả cuối cùng vào mạng
    reluctance_network.loop_flux.data = current_phi
    reluctance_network.add_elements_lite()
    
    if debug:
        print("--- Iteration Finished ---")
        
    return reluctance_network