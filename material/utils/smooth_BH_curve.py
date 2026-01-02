import numpy as np
from scipy.interpolate import UnivariateSpline, PchipInterpolator, interp1d

def smooth_BH_curve(iron, num_points=1000): 
    # Hằng số độ từ thẩm chân không
    mu_0 = 4 * np.pi * 1e-7
    
    B_raw = iron.B_H_curve["B_data"]
    H_raw = iron.B_H_curve["H_data"]
    
    # --- BƯỚC 1: TÍNH TOÁN ĐỘ TỪ THẨM TƯƠNG ĐỐI (mu_r) THÔ ---
    with np.errstate(divide='ignore', invalid='ignore'):
        mu_r_raw = B_raw / (mu_0 * H_raw)
    
    if len(B_raw) > 1:
        # Xử lý điểm (0,0) dựa trên độ dốc điểm kế tiếp
        mu_r_raw[0] = (B_raw[1] / H_raw[1]) / mu_0

    # --- BƯỚC 2: LÀM MƯỢT ĐẠO HÀM d(mu_r)/dB ---
    dmu_db_raw = np.gradient(mu_r_raw, B_raw)
    temp_interp = PchipInterpolator(B_raw, dmu_db_raw)
    
    # Tạo lưới điểm thưa để lấy mẫu đạo hàm
    num_sparse_points = 18 
    B_sparse = np.linspace(0.15, B_raw.max(), num_sparse_points)
    dmu_sparse = temp_interp(B_sparse)

    # Thêm điểm gốc và đối xứng gương để đảm bảo tính liên tục tại gốc tọa độ
    B_sparse = np.insert(B_sparse, 0, 0.0)
    dmu_sparse = np.insert(dmu_sparse, 0, 0.0)
    B_mirror = np.concatenate((-B_sparse[::-1], B_sparse))
    dmu_mirror = np.concatenate((-dmu_sparse[::-1], dmu_sparse))
    
    _, idx = np.unique(B_mirror, return_index=True)
    B_mirror, dmu_mirror = B_mirror[np.sort(idx)], dmu_mirror[np.sort(idx)]

    # Tạo Spline cho đạo hàm
    deriv_spline = UnivariateSpline(B_mirror, dmu_mirror, k=3, s=0)

    # --- BƯỚC 3: TÍCH PHÂN NGƯỢC ĐỂ LẤY mu_r MƯỢT ---
    B_anchor = np.linspace(B_raw.min(), B_raw.max(), 50)
    mu_antiderivative = deriv_spline.antiderivative()
    mu_initial = mu_r_raw[0]
    mu_anchor = mu_antiderivative(B_anchor) - mu_antiderivative(0) + mu_initial

    # --- BƯỚC 4: NÂNG CẤP ĐỘ PHÂN GIẢI LÊN 1000 ĐIỂM ---
    B_final = np.linspace(B_raw.min(), B_raw.max(), num_points)
    f_mu_interp = interp1d(B_anchor, mu_anchor, kind='quadratic', fill_value="extrapolate")
    mu_r_smooth = f_mu_interp(B_final)

    # --- BƯỚC 5: ÉP BÃO HÒA VỀ 1.0 MỘT CÁCH MƯỢT MÀ (KHÔNG GÃY) ---
    def smooth_saturation(mu_in, B_in, B_max):
        # Bắt đầu ép từ 85% dải B bão hòa
        B_start_sat = 0.85 * B_max
        width = B_max - B_start_sat
        
        # Hàm trọng số Cosine để đạo hàm liên tục tại điểm tiếp giáp
        weight = np.clip((B_in - B_start_sat) / width, 0, 1)
        weight = 0.5 * (1 - np.cos(weight * np.pi)) 
        
        return mu_in * (1 - weight) + 1.0 * weight

    mu_r_final = smooth_saturation(mu_r_smooth, B_final, B_final.max())
    # Đảm bảo sàn vật lý mu_r >= 1
    mu_r_final = np.maximum(mu_r_final, 1.0)

    # --- BƯỚC 6: TÍNH TOÁN LẠI H TỪ DỮ LIỆU ĐÃ LÀM MƯỢT ---
    H_final = np.zeros_like(B_final)
    with np.errstate(divide='ignore', invalid='ignore'):
        H_final[1:] = B_final[1:] / (mu_0 * mu_r_final[1:])
    H_final[0] = 0.0

    # --- BƯỚC 7: CẬP NHẬT DATABASE VÀ TỰ ĐỘNG BACKUP ---
    # Cập nhật dữ liệu hiện tại
    iron.B_H_curve["B_data"] = B_final
    iron.B_H_curve["H_data"] = H_final
    
    # SAU KHI LÀM MƯỢT XONG MỚI BACKUP: Đây sẽ là dữ liệu chuẩn nhất cho mọi thuật toán sau này
    iron.backup_B_H_curve = {
        "B_data": iron.B_H_curve["B_data"].copy(),
        "H_data": iron.B_H_curve["H_data"].copy()
    }
    
    return iron