import numpy as np
import matplotlib.pyplot as plt
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
from dataclasses import dataclass
from typing import Any, List

@dataclass
class SolverResult:
    potential: np.ndarray
    residual_history: List[float]
    figure: Any

def solve_magnetic_equation(reluctance_network, 
                            method="conjugate_gradient",
                            max_iteration=50, 
                            max_relative_residual=1e-4, 
                            max_damping=0.5,
                            load_step=5, 
                            debug=True):

    # 1. Reset trạng thái mạng từ trở
    reluctance_network.set_reluctance_at_zero()
    reluctance_network.magnetic_potential.data *= 0 
    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)

    divergence_count_max = 10

    # Xử lý tham số max_iteration nếu là tuple
    if isinstance(max_iteration, tuple):
        max_iteration = max_iteration[0]

    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()
    checkpoint_potential = None
    
    load_factors = np.linspace(0, 1, load_step + 1)[1:]
    residual_history = []
    load_step_indices = []

    # Khởi tạo damping ban đầu
    current_damping = max_damping
    divergence_count = 0

    for i in range(load_step):
        current_load = load_factors[i]
        prev_direction = None
        prev_z = None
        prev_res = None
        divergence_count = 0
        
        # Reset damping về max_damping cho mỗi bước tăng tải mới
        current_damping = max_damping
        
        for j in range(max_iteration):
            if j == 0 and i > 0:
                load_step_indices.append(len(residual_history))

            # Tạo phương trình thế từ
            comp = reluctance_network.create_magnetic_potential_equation(
                first_time=(i == 0 and j == 0),
                load_factor=current_load,
                debug=False
            )
            
            G, J = comp.G, comp.J
            P_active = current_magnetic_potential.flatten(order='F')[:-1]

            # Lựa chọn phương pháp giải
            if method == "fixed_point_iteration":
                p_sol = spsolve(G, J)
                p_full = np.append(p_sol, 0.0).reshape(magnetic_potential_shape, order='F')
                res_val = np.linalg.norm(p_full - current_magnetic_potential) / (np.linalg.norm(p_full) + 1e-12)
                direction = p_full - current_magnetic_potential
            
            elif method == "conjugate_gradient":
                res = J - G.dot(P_active)
                res_val = np.linalg.norm(res) / (np.linalg.norm(J) + 1e-12)
                z = spsolve(G, res)
                
                if prev_direction is None:
                    direction = z
                else:
                    # Polak-Ribière Conjugate Gradient
                    beta = np.dot(z, res - prev_res) / (np.dot(prev_z, prev_res) + 1e-15)
                    beta = max(0, beta)
                    direction = z + beta * prev_direction
            
            # --- Logic Adaptive Damping mới ---
            if len(residual_history) > 0 and res_val > residual_history[-1]:
                # Nếu sai số tăng (phân kỳ), lưu lại điểm an toàn và giảm damping
                if divergence_count == 0:
                    checkpoint_potential = current_magnetic_potential.copy()
                
                divergence_count += 1
                current_damping *= 0.5  # Giảm 1 nửa damping theo yêu cầu
                prev_direction = None   # Reset hướng CG để tránh cộng dồn sai số
                

                # Nếu phân kỳ quá 10 lần, quay về checkpoint và kết thúc bước tải này
                
                if divergence_count >= divergence_count_max:
                    current_magnetic_potential = checkpoint_potential.copy()
                    reluctance_network.magnetic_potential.data = current_magnetic_potential
                    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                    break
                continue
            else:
                divergence_count = 0

            # Cập nhật lịch sử và trạng thái
            residual_history.append(res_val)
            
            if method == "conjugate_gradient":
                prev_z = z
                prev_res = res.copy()
                prev_direction = direction

            # Thực hiện bước nhảy với damping
            active_update = P_active + current_damping * direction.flatten(order='F')[:P_active.size]
            next_p = np.append(active_update, 0.0).reshape(magnetic_potential_shape, order='F')

            current_magnetic_potential = next_p
            reluctance_network.magnetic_potential.data = current_magnetic_potential
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)

            # Kiểm tra điều kiện hội tụ
            if res_val < max_relative_residual:
                break

    # Vẽ đồ thị hội tụ
    fig, ax = plt.subplots(figsize=(10, 6))
    if debug and len(residual_history) > 0: 
        ax.plot(residual_history, label=f"Method: {method}", marker='o', markersize=3)
        for idx in load_step_indices:
            ax.axvline(x=idx, color='r', linestyle='--', alpha=0.5)
        ax.set_yscale('log')
        ax.set_xlabel("Total Cumulative Iterations")
        ax.set_ylabel("Relative Residual (Log scale)")
        ax.set_title(f"Convergence History (max_damping={max_damping}), divergence count max = {divergence_count_max}")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        plt.show()

    reluctance_network.add_elements_lite()
    return SolverResult(potential=current_magnetic_potential, 
                        residual_history=residual_history, 
                        figure=fig)