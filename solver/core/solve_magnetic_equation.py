import numpy as np
import matplotlib.pyplot as plt
import scipy.sparse as sp  # BỔ SUNG: Khai báo sp để dùng cho LM
from scipy.sparse.linalg import spsolve, MatrixRankWarning
from tqdm import tqdm
import warnings

def solve_magnetic_equation(reluctance_network, 
                            method = "fixed_point_iteration",
                            max_iteration=50, 
                            max_relative_residual=1e-4, 
                            adaptive_damping_factor = (1.0, 0.1),
                            load_step=5, 
                            debug=True):
    
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()
    load_factors = np.linspace(0, 1, load_step + 1)[1:]
    residual_history = []

    if debug:
        print(f"Starting Solver using {method} (Load Steps: {load_step})")

    for i in range(load_step):
        current_load = load_factors[i]
        
        for j in range(max_iteration):
            current_damping = adaptive_damping_factor[0] if j == 0 else adaptive_damping_factor[1]
            first_time = (i == 0 and j == 0)
            
            # Tạo phương trình (G, J, Ja) từ logic Golden Code
            equation_component = reluctance_network.create_magnetic_potential_equation(
                first_time=first_time,
                load_factor=current_load,
                debug=False
            )
            
            G = equation_component.G
            J = equation_component.J
            P_active = current_magnetic_potential.flatten(order='F')[:-1]

            # --- CÁC PHƯƠNG PHÁP GIẢI ---
            if method == "fixed_point_iteration":
                try:
                    solved_vector = spsolve(G, J)
                    solved_vector_with_ref = np.append(solved_vector, 0.0)
                    P_solved = solved_vector_with_ref.reshape(magnetic_potential_shape, order='F')
                    norm_val = np.linalg.norm(P_solved)
                    current_residual = np.linalg.norm(P_solved - current_magnetic_potential) / norm_val if norm_val > 1e-12 else 0.0
                    next_magnetic_potential = (current_magnetic_potential * (1 - current_damping) + 
                                               P_solved * current_damping)
                except Exception as e:
                    print(f"FPI Error: {e}")
                    return current_magnetic_potential

            elif method == "newton_raphson":
                Ja = equation_component.Ja
                residual_vector = J - G.dot(P_active)
                source_norm = np.linalg.norm(J) if np.linalg.norm(J) > 1e-12 else 1.0
                current_residual = np.linalg.norm(residual_vector) / source_norm
                
                if current_residual < max_relative_residual:
                    residual_history.append(current_residual)
                    break

                try:
                    delta_P = spsolve(Ja, residual_vector)
                    P_active_next = P_active + current_damping * delta_P
                    next_magnetic_potential = np.append(P_active_next, 0.0).reshape(magnetic_potential_shape, order='F')
                except Exception as e:
                    print(f"NR Error: {e}")
                    return current_magnetic_potential

            elif method == "direct_optimization":
                residual_vector = J - G.dot(P_active)
                source_norm = np.linalg.norm(J) if np.linalg.norm(J) > 1e-12 else 1.0
                current_residual = np.linalg.norm(residual_vector) / source_norm

                if current_residual < max_relative_residual:
                    residual_history.append(current_residual)
                    break

                try:
                    search_direction = spsolve(G, residual_vector)
                    P_active_next = P_active + current_damping * search_direction
                    next_magnetic_potential = np.append(P_active_next, 0.0).reshape(magnetic_potential_shape, order='F')
                except Exception as e:
                    print(f"Optimization Error: {e}")
                    return current_magnetic_potential

            elif method == "levenberg_marquardt":
                Ja = equation_component.Ja
                residual_vector = J - G.dot(P_active)
                source_norm = np.linalg.norm(J) if np.linalg.norm(J) > 1e-12 else 1.0
                current_residual = np.linalg.norm(residual_vector) / source_norm

                if current_residual < max_relative_residual:
                    residual_history.append(current_residual)
                    break

                try:
                    # LM Logic: Ja_augmented = Ja + lambda * diag(Ja)
                    lambda_val = current_residual * 0.1 
                    # SỬA LỖI: Đã có sp.diags sau khi import scipy.sparse as sp
                    diag_damping = sp.diags(Ja.diagonal() * lambda_val)
                    
                    delta_P = spsolve(Ja + diag_damping, residual_vector)
                    
                    P_active_next = P_active + current_damping * delta_P
                    next_magnetic_potential = np.append(P_active_next, 0.0).reshape(magnetic_potential_shape, order='F')
                except Exception as e:
                    print(f"LM Error: {e}")
                    return current_magnetic_potential

            # 5. Lưu lịch sử và cập nhật trạng thái
            residual_history.append(current_residual)
            current_magnetic_potential = next_magnetic_potential
            reluctance_network.magnetic_potential.data = current_magnetic_potential
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)

            if current_residual < max_relative_residual:
                break

            if debug and j % 10 == 0:
                print(f"   Load {current_load:.2f} | Iter {j}: Residual={current_residual:.2e}")

    # 6. Trực quan hóa kết quả hội tụ
    if debug and len(residual_history) > 1:
        if len(residual_history) > 2:
            residual_history[0] = 2 * residual_history[1] - residual_history[2]

        plt.figure(figsize=(10, 6))
        plt.plot(residual_history, label=f'Residual ({method})', marker='.', markersize=4)
        plt.yscale('log')
        plt.title(f'Convergence History: {method}')
        plt.xlabel('Total Cumulative Iterations')
        plt.ylabel('Relative Residual (Log scale)')
        plt.grid(True, which="both", alpha=0.3)
        plt.legend()
        plt.show()

    return current_magnetic_potential