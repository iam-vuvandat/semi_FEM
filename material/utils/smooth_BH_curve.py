import numpy as np
from scipy.interpolate import UnivariateSpline, PchipInterpolator

def smooth_BH_curve(iron, num_points=3000):
    mu_0 = 4 * np.pi * 1e-7
    
    B_raw = iron.B_H_curve["B_data"]
    H_raw = iron.B_H_curve["H_data"]
    
    # --- BƯỚC 1: TÍNH TOÁN MU VÀ ĐẠO HÀM THÔ ---
    with np.errstate(divide='ignore', invalid='ignore'):
        mu_r_raw = B_raw / (mu_0 * H_raw)
    
    # Xử lý điểm 0
    if len(B_raw) > 1:
        mu_r_raw[0] = (B_raw[1] / H_raw[1]) / mu_0

    # Tính đạo hàm thô (Gradient)
    dmu_db_raw = np.gradient(mu_r_raw, B_raw)

    # --- BƯỚC 2: GIẢM SỐ ĐIỂM (DOWNSAMPLING) ---
    # Ta dùng Pchip tạm thời để lấy mẫu giá trị tại các vị trí mong muốn
    temp_interp = PchipInterpolator(B_raw, dmu_db_raw)
    
    # CHÌA KHÓA KHỬ NHIỄU: Chỉ lấy 15-18 điểm đại diện.
    # Số lượng ít điểm ép đường cong phải "trơn", không thể rung lắc.
    # Bắt đầu lấy từ 0.15 để né hoàn toàn nhiễu ở gốc.
    num_sparse_points = 18 
    B_sparse = np.linspace(0.15, B_raw.max(), num_sparse_points)
    
    # Lấy giá trị đạo hàm tại các điểm thưa này
    dmu_sparse = temp_interp(B_sparse)

    # --- BƯỚC 3: XỬ LÝ ĐIỂM 0 VÀ ĐỐI XỨNG ---
    # Thêm thủ công điểm (0,0) vào tập dữ liệu thưa -> Đảm bảo đạo hàm tại gốc = 0
    B_sparse = np.insert(B_sparse, 0, 0.0)
    dmu_sparse = np.insert(dmu_sparse, 0, 0.0)

    # Tạo đối xứng LẺ (Odd Symmetry) cho đạo hàm
    # f'(-x) = -f'(x)
    B_mirror = np.concatenate((-B_sparse[::-1], B_sparse))
    dmu_mirror = np.concatenate((-dmu_sparse[::-1], dmu_sparse))
    
    # Loại bỏ các điểm trùng nhau tại 0 (nếu có)
    _, idx = np.unique(B_mirror, return_index=True)
    B_mirror = B_mirror[np.sort(idx)]
    dmu_mirror = dmu_mirror[np.sort(idx)]

    # --- BƯỚC 4: NỘI SUY (INTERPOLATION) ---
    # Dùng s=0 (Interpolation) thay vì Smoothing.
    # Vì tập điểm B_sparse đã được lọc kỹ và rất thưa, ta tin tưởng nó hoàn toàn.
    deriv_spline = UnivariateSpline(B_mirror, dmu_mirror, k=3, s=0)

    # --- BƯỚC 5: TÍCH PHÂN ĐỂ TÁI TẠO MU ---
    B_final = np.linspace(B_raw.min(), B_raw.max(), num_points)
    
    # Nguyên hàm của đạo hàm chính là hàm Mu
    mu_antiderivative = deriv_spline.antiderivative()
    
    # Tính Mu(B) = Integral(dMu) + Mu_initial
    mu_initial = mu_r_raw[0]
    mu_r_final = mu_antiderivative(B_final) - mu_antiderivative(0) + mu_initial

    # --- BƯỚC 6: CẬP NHẬT DỮ LIỆU ---
    H_final = np.zeros_like(B_final)
    H_final[1:] = B_final[1:] / (mu_0 * mu_r_final[1:])
    H_final[0] = 0

    iron.B_H_curve["B_data"] = B_final
    iron.B_H_curve["H_data"] = H_final