import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def conjugate_gradient(reluctance_network, 
                       max_iteration=50, 
                       max_relative_residual=1e-4, 
                       adaptive_damping_factor=(1.0, 0.1),
                       load_step=5, 
                       debug=True):
    """
    Giải hệ phương trình mạng điện trở từ bằng phương pháp Conjugate Gradient (CG).
    Hàm xử lý độc lập, cập nhật trực tiếp vào đối tượng reluctance_network và không return.
    """

    # --- 1. Khởi tạo và Reset mạng ---
    reluctance_network.set_reluctance_at_zero()
    reluctance_network.magnetic_potential.data *= 0 
    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)

    if isinstance(max_iteration, tuple):
        max_iteration = max_iteration[0]

    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()
    checkpoint_potential = None
    
    load_factors = np.linspace(0, 1, load_step + 1)[1:]
    residual_history = []
    load_step_indices = []

    # --- 2. Vòng lặp Load Steps ---
    for i in range(load_step):
        current_load = load_factors[i]
        divergence_count = 0
        current_damping = adaptive_damping_factor[0]
        
        # Các biến trạng thái của Conjugate Gradient (Reset mỗi Load Step)
        prev_direction = None
        prev_z = None
        prev_res = None
        
        # --- 3. Vòng lặp Iteration ---
        for j in range(max_iteration):
            if j == 0 and i > 0:
                load_step_indices.append(len(residual_history))

            if j == 0:
                current_damping = adaptive_damping_factor[0]
            elif j == 1:
                current_damping = adaptive_damping_factor[1]
            
            # Tạo hệ phương trình G * P = J
            comp = reluctance_network.create_magnetic_potential_equation(
                first_time=(i == 0 and j == 0),
                load_factor=current_load,
                debug=False
            )
            G, J = comp.G, comp.J
            
            # P_active: Vector tiềm năng hiện tại (bỏ nút tham chiếu cuối cùng)
            P_active = current_magnetic_potential.flatten(order='F')[:-1]

            # --- Thuật toán Conjugate Gradient ---
            # Tính sai số dư (Residual vector): r = J - G * P
            res = J - G.dot(P_active)
            res_val = np.linalg.norm(res) / (np.linalg.norm(J) + 1e-12)
            
            # Giải hệ bổ trợ (Preconditioning step): G * z = r
            z = spsolve(G, res)
            
            if prev_direction is None:
                direction = z
            else:
                # Sử dụng công thức Polak-Ribière để tính Beta
                # $\beta = \frac{z_{j}^T (res_{j} - res_{j-1})}{z_{j-1}^T res_{j-1}}$
                numerator = np.dot(z, res - prev_res)
                denominator = np.dot(prev_z, prev_res) + 1e-15
                beta = max(0, numerator / denominator)
                direction = z + beta * prev_direction

            # --- 4. Kiểm tra phân kỳ (Divergence Handling) ---
            if len(residual_history) > 0 and res_val > residual_history[-1]:
                if divergence_count == 0:
                    checkpoint_potential = current_magnetic_potential.copy()
                
                divergence_count += 1
                current_damping *= 0.5
                prev_direction = None # Reset hướng khi phân kỳ
                
                if divergence_count >= 3:
                    current_magnetic_potential = checkpoint_potential.copy()
                    reluctance_network.magnetic_potential.data = current_magnetic_potential
                    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                    break
                continue
            else:
                divergence_count = 0

            residual_history.append(res_val)

            # --- 5. Cập nhật trạng thái và Potentials ---
            prev_z = z
            prev_res = res.copy()
            prev_direction = direction

            # Cập nhật tiềm năng mới
            active_update = P_active + current_damping * direction
            next_p = np.append(active_update, 0.0).reshape(magnetic_potential_shape, order='F')

            current_magnetic_potential = next_p
            reluctance_network.magnetic_potential.data = current_magnetic_potential
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)

            if res_val < max_relative_residual:
                break

    # --- 6. Trực quan hóa ---
    fig, ax = plt.subplots(figsize=(10, 6))
    if len(residual_history) > 2:
        residual_history[0] = 2 * residual_history[1] - residual_history[2]

    if debug: 
        ax.plot(residual_history, label="Conjugate Gradient", color='orangered', marker='o', markersize=3)
        for idx in load_step_indices:
            ax.axvline(x=idx, color='gray', linestyle='--', alpha=0.5)
        ax.set_yscale('log')
        ax.set_xlabel("Total Cumulative Iterations")
        ax.set_ylabel("Relative Residual (Log scale)")
        ax.set_title("Convergence History: Conjugate Gradient Method")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        plt.show()
    else:
        plt.close(fig)

    reluctance_network.add_elements_lite()