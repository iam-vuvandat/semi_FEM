import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve, MatrixRankWarning
from tqdm import tqdm
import warnings

def solve_magnetic_equation(reluctance_network, 
                            max_iteration=50, 
                            max_relative_residual=1e-4, 
                            adaptive_damping_factor = (0.6,0.06),
                            load_step=5, 
                            debug=True):
    
    # 1. Chuẩn bị dữ liệu
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()
    
    # Tạo mảng các mức tải: [0.2, 0.4, ..., 1.0]
    load_factors = np.linspace(0, 1, load_step+1)[1:]
    
    # [TỐI ƯU] Tính trước mảng Damping cho từng mức tải ngay từ đầu
    # Thay vì tính lại 250 lần trong hàm con
    adaptive_dampings = np.linspace(adaptive_damping_factor[0], adaptive_damping_factor[1], load_step + 1)[1:]
    print(adaptive_dampings)
    residual_history = []

    # 2. Bắt đầu vòng lặp tải
    for i in range(load_step):
        current_load = load_factors[i]
        target_damping = adaptive_dampings[i] # Damping mục tiêu cho mức tải này
        
        if debug:
            print(f"--- Load Step: {current_load:.2f} | Target Damping: {target_damping:.3f} ---")

        # 3. Vòng lặp giải (Solver Loop)
        for j in range(max_iteration):
            # Logic Adaptive Damping:
            # Bước đầu của mỗi tải (j=0) luôn đi nhẹ (first_step) để tránh sốc
            # Các bước sau (j>0) dùng damping đã tính trước
            if j == 0:
                current_damping = 1.0 # gán cứng, đúng logic 
            else:
                current_damping = target_damping * 0.8 * j

            # Logic Warm Start: Chỉ reset ở giây phút đầu tiên của toàn bộ quá trình
            if i == 0 and j == 0:
                first_time = True
            else:
                first_time = False
            
            # Tạo phương trình
            equation_component = reluctance_network.create_magnetic_potential_equation(
                first_time=first_time,
                load_factor=current_load
            )
            G = equation_component.G
            J = equation_component.J

            # Giải hệ phương trình tuyến tính
            try:
                solved_vector = spsolve(G, J)
            except Exception as e:
                print(f"Solver Error at Load {current_load}, Iter {j}: {e}")
                return # Thoát nếu lỗi ma trận

            # Xử lý vector kết quả
            solved_vector_with_ref = np.append(solved_vector, 0.0)
            magnetic_potential_solved = solved_vector_with_ref.reshape(magnetic_potential_shape, order='F')
            
            # Cập nhật nghiệm với Damping (Relaxation)
            next_magnetic_potential = (current_magnetic_potential * (1 - current_damping) + 
                                       magnetic_potential_solved * current_damping)
            
            # Tính sai số (Residual)
            if i == 0 and j == 0:
                current_residual = 0.0
            else:
                norm_next = np.linalg.norm(next_magnetic_potential)
                if norm_next == 0:
                    current_residual = 0.0
                else:
                    current_residual = np.linalg.norm(next_magnetic_potential - current_magnetic_potential) / norm_next
            
            residual_history.append(current_residual)
            
            # In debug gọn gàng hơn
            if debug and j % 10 == 0: # Chỉ in mỗi 10 vòng lặp để đỡ spam
                print(f"   Iter {j}: Residual={current_residual:.2e}, Damping={current_damping:.2f}")

            # Cập nhật trạng thái cho vòng sau
            current_magnetic_potential = next_magnetic_potential
            reluctance_network.magnetic_potential.data = next_magnetic_potential
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)

    # 4. Vẽ đồ thị
    if debug:
        plt.figure(figsize=(10, 6))
        plt.plot(residual_history, label='Residual')
        plt.yscale('log')
        plt.title('Relative Residual History')
        plt.xlabel('Total Iterations')
        plt.ylabel('Residual (Log scale)')
        plt.grid(True, which="both", alpha=0.3)
        
        # Vẽ vạch đỏ phân chia các mức tải
        for k in range(1, load_step):
            plt.axvline(x=k*max_iteration, color='r', linestyle='--', alpha=0.5)
            
        plt.legend()
        plt.show()