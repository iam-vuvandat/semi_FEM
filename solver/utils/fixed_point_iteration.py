import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def fix_point_iteration(reluctance_network, 
                        max_iteration=50, 
                        max_relative_residual=1e-4, 
                        adaptive_damping_factor=(1.0, 0.1),
                        load_step=5, 
                        debug=True):
    """
    Thực hiện giải hệ phương trình mạng điện trở từ bằng phương pháp lặp điểm cố định (Fixed-point iteration).
    Hàm này tự quản lý toàn bộ vòng lặp load step, hội tụ và cập nhật trực tiếp vào mạng.
    """

    # --- 1. Khởi tạo trạng thái ban đầu ---
    reluctance_network.set_reluctance_at_zero()
    # Reset potential về 0
    reluctance_network.magnetic_potential.data *= 0 
    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)

    # Xử lý trường hợp max_iteration được truyền dưới dạng tuple
    if isinstance(max_iteration, tuple):
        max_iteration = max_iteration[0]

    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()
    checkpoint_potential = None
    
    # Thiết lập các bước tải (load steps)
    load_factors = np.linspace(0, 1, load_step + 1)[1:]
    residual_history = []
    load_step_indices = []
    
    current_damping = adaptive_damping_factor[0]
    divergence_count = 0

    # --- 2. Vòng lặp Load Steps (Tăng dần tải trọng) ---
    for i in range(load_step):
        current_load = load_factors[i]
        divergence_count = 0
        
        # --- 3. Vòng lặp Iteration (Lặp phi tuyến) ---
        for j in range(max_iteration):
            # Đánh dấu vị trí bắt đầu load step mới trên đồ thị
            if j == 0 and i > 0:
                load_step_indices.append(len(residual_history))

            # Thiết lập damping factor theo số bước lặp
            if j == 0:
                current_damping = adaptive_damping_factor[0]
            elif j == 1:
                current_damping = adaptive_damping_factor[1]
            
            # Tạo phương trình từ tính tại điểm làm việc hiện tại
            comp = reluctance_network.create_magnetic_potential_equation(
                first_time=(i == 0 and j == 0),
                load_factor=current_load,
                debug=False
            )
            
            G, J = comp.G, comp.J

            # Giải hệ phương trình tuyến tính: G * p = J
            p_sol = spsolve(G, J)
            
            # Khôi phục vector đầy đủ (thêm nút tham chiếu 0.0 vào cuối)
            p_full = np.append(p_sol, 0.0).reshape(magnetic_potential_shape, order='F')
            
            # Tính sai số dư tương đối (Residual) dựa trên sự thay đổi tiềm năng
            res_val = np.linalg.norm(p_full - current_magnetic_potential) / (np.linalg.norm(p_full) + 1e-12)
            
            # Hướng cập nhật
            direction = p_full - current_magnetic_potential

            # --- 4. Xử lý phân kỳ (Divergence Handling) ---
            if len(residual_history) > 0 and res_val > residual_history[-1]:
                if divergence_count == 0:
                    checkpoint_potential = current_magnetic_potential.copy()
                
                divergence_count += 1
                current_damping *= 0.5  # Giảm damping để cố gắng ổn định hệ thống
                
                if divergence_count >= 3:
                    # Nếu phân kỳ quá 3 lần, quay lại checkpoint và dừng load step này
                    current_magnetic_potential = checkpoint_potential.copy()
                    reluctance_network.magnetic_potential.data = current_magnetic_potential
                    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                    break 
                continue
            else:
                divergence_count = 0

            residual_history.append(res_val)

            # --- 5. Cập nhật kết quả vào đối tượng mạng ---
            # Cập nhật tiềm năng: p_mới = p_cũ + damping * (p_giải_được - p_cũ)
            current_magnetic_potential = current_magnetic_potential + current_damping * direction
            
            # Ghi đè dữ liệu vào đối tượng gốc
            reluctance_network.magnetic_potential.data = current_magnetic_potential
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)

            # Kiểm tra điều kiện hội tụ
            if res_val < max_relative_residual:
                break

    # --- 6. Hậu xử lý và Trực quan hóa ---
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Làm mượt điểm đầu đồ thị để hiển thị scale log đẹp hơn
    if len(residual_history) > 2:
        residual_history[0] = 2 * residual_history[1] - residual_history[2]

    if debug: 
        ax.plot(residual_history, label="Fixed Point Iteration", color='teal', marker='o', markersize=3)
        for idx in load_step_indices:
            ax.axvline(x=idx, color='red', linestyle='--', alpha=0.5, label='New Load Step' if idx == load_step_indices[0] else "")
        
        ax.set_yscale('log')
        ax.set_xlabel("Total Cumulative Iterations")
        ax.set_ylabel("Relative Residual (Log scale)")
        ax.set_title("Convergence History: Fixed Point Method")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        plt.show()
    else:
        plt.close(fig)

    # Cập nhật các thành phần phụ trợ cuối cùng của mạng
    reluctance_network.add_elements_lite()
    
    # Không return gì