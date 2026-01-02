import numpy as np

def step_permeability(iron, load_factor=0.1):
    """
    Can thiệp vào vật liệu bằng thuật toán Stretching (Kéo giãn).
    Đảm bảo mu_r luôn >= 1.05 và thay đổi mượt mà theo load_factor.
    """
    mu_0 = 4 * np.pi * 1e-7
    floor_mu_r = 1.05  # Sàn an toàn mới theo yêu cầu của bạn
    
    # 1. Truy xuất dữ liệu mượt từ Backup
    B_orig = iron.backup_B_H_curve["B_data"]
    H_orig = iron.backup_B_H_curve["H_data"]
    
    # 2. Tính toán mu_r gốc chuẩn
    with np.errstate(divide='ignore', invalid='ignore'):
        mu_r_orig = B_orig / (mu_0 * H_orig)
    
    if len(mu_r_orig) > 1:
        mu_r_orig[0] = mu_r_orig[1]

    # 3. THUẬT TOÁN KÉO GIÃN (STRETCHING)
    # Công thức này đảm bảo tại điểm bão hòa (mu_r=1.05) thì mu_r_step vẫn là 1.05
    # Các điểm có mu_r cao sẽ bị kéo giãn mạnh hơn.
    mu_r_step = floor_mu_r + (mu_r_orig - floor_mu_r) * load_factor
    
    # 4. CHỐT CHẶN VẬT LÝ (An toàn tuyệt đối)
    # Đảm bảo không có sai số nội suy nào làm mu_r thấp hơn floor
    mu_r_clamped = np.maximum(mu_r_step, floor_mu_r)

    # 5. Tính toán lại H mới dựa trên mu_r đã kéo giãn
    H_final = np.zeros_like(B_orig)
    with np.errstate(divide='ignore', invalid='ignore'):
        # H = B / (mu_0 * mu_r_clamped)
        H_final[1:] = B_orig[1:] / (mu_0 * mu_r_clamped[1:])
    H_final[0] = 0.0

    # 6. Cập nhật dữ liệu làm việc
    iron.B_H_curve["B_data"] = B_orig.copy()
    iron.B_H_curve["H_data"] = H_final

    return iron