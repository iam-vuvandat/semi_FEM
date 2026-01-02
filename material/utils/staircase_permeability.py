import numpy as np

def staircase_permeability(iron, num_steps=8):
    """
    Tạo đường cong B-H bậc thang dựa trên dữ liệu đã được làm mượt trong bản backup.
    Không thực hiện backup mới, chỉ đọc từ iron.backup_B_H_curve.
    """
    # 1. TRUY XUẤT DỮ LIỆU TỪ BACKUP (Dữ liệu đã smooth 1000 điểm)
    B_orig = iron.backup_B_H_curve["B_data"]
    H_orig = iron.backup_B_H_curve["H_data"]
    
    # 2. Tính toán độ từ thẩm tương đối (mu_r) thực tế từ bản backup
    mu_0 = 4 * np.pi * 1e-7
    with np.errstate(divide='ignore', invalid='ignore'):
        mu_real = B_orig / (mu_0 * H_orig)
    
    if len(mu_real) > 1:
        mu_real[0] = mu_real[1] # Xử lý điểm gốc (0,0)

    # 3. Xác định dải giá trị mu_r để chia bậc
    mu_min = np.min(mu_real)
    mu_max = np.max(mu_real)
    
    # 4. Tạo các mức bậc thang (levels) đều nhau
    levels = np.linspace(mu_min, mu_max, num_steps)
    
    # ÉP SÀN VẬT LÝ: Bậc thấp nhất luôn là 1.0 (không khí)
    levels[0] = 1.0
    
    # 5. Ánh xạ (Quantization) từng điểm mu_real vào bậc thang gần nhất
    # Sử dụng list comprehension kết hợp argmin để tìm mức mu_staircase
    mu_staircase = np.array([levels[np.abs(levels - m).argmin()] for m in mu_real])
    
    # 6. Tính toán lại H_staircase để khớp với các mặt phẳng mu bậc thang
    H_staircase = np.zeros_like(H_orig)
    mask = mu_staircase > 0
    with np.errstate(divide='ignore', invalid='ignore'):
        H_staircase[mask] = B_orig[mask] / (mu_0 * mu_staircase[mask])
    
    # 7. CẬP NHẬT VÀO ĐƯỜNG CONG LÀM VIỆC (Working Curve)
    # Solver sẽ đọc dữ liệu này để tính toán ma trận từ trở
    iron.B_H_curve["B_data"] = B_orig.copy()
    iron.B_H_curve["H_data"] = H_staircase

    return iron