import numpy as np
from scipy.interpolate import UnivariateSpline, PchipInterpolator, interp1d

def smooth_BH_curve(iron, num_points=1000): 
    mu_0 = 4 * np.pi * 1e-7
    
    B_raw = iron.B_H_curve["B_data"]
    H_raw = iron.B_H_curve["H_data"]
    
  
    with np.errstate(divide='ignore', invalid='ignore'):
        mu_r_raw = B_raw / (mu_0 * H_raw)
    
    if len(B_raw) > 1:
        mu_r_raw[0] = (B_raw[1] / H_raw[1]) / mu_0

    dmu_db_raw = np.gradient(mu_r_raw, B_raw)
    temp_interp = PchipInterpolator(B_raw, dmu_db_raw)
    
    num_sparse_points = 18 
    B_sparse = np.linspace(0.15, B_raw.max(), num_sparse_points)
    dmu_sparse = temp_interp(B_sparse)

    B_sparse = np.insert(B_sparse, 0, 0.0)
    dmu_sparse = np.insert(dmu_sparse, 0, 0.0)

    B_mirror = np.concatenate((-B_sparse[::-1], B_sparse))
    dmu_mirror = np.concatenate((-dmu_sparse[::-1], dmu_sparse))
    
    _, idx = np.unique(B_mirror, return_index=True)
    B_mirror = B_mirror[np.sort(idx)]
    dmu_mirror = dmu_mirror[np.sort(idx)]

    deriv_spline = UnivariateSpline(B_mirror, dmu_mirror, k=3, s=0)

   
    B_anchor = np.linspace(B_raw.min(), B_raw.max(), 50)
    mu_antiderivative = deriv_spline.antiderivative()
    
    mu_initial = mu_r_raw[0]
    mu_anchor = mu_antiderivative(B_anchor) - mu_antiderivative(0) + mu_initial

    # --- BƯỚC 6: NỘI SUY BẬC 2 NÂNG LÊN 1000 ĐIỂM (Yêu cầu mới) ---
    # Tạo lưới 1000 điểm
    B_final = np.linspace(B_raw.min(), B_raw.max(), num_points)
    
    # Sử dụng nội suy bậc 2 (quadratic) để nâng số điểm
    f_mu_interp = interp1d(B_anchor, mu_anchor, kind='quadratic', fill_value="extrapolate")
    mu_r_final = f_mu_interp(B_final)

    # --- BƯỚC 7: CẬP NHẬT DỮ LIỆU CUỐI CÙNG ---
    H_final = np.zeros_like(B_final)
    # Tránh chia cho 0 tại gốc
    H_final[1:] = B_final[1:] / (mu_0 * mu_r_final[1:])
    H_final[0] = 0

    iron.B_H_curve["B_data"] = B_final
    iron.B_H_curve["H_data"] = H_final