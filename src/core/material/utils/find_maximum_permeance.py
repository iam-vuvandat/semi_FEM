import numpy as np
from scipy.interpolate import interp1d
from dataclasses import dataclass

MU0 = 4 * np.pi * 1e-7  # H/m

# --- 1. ĐỊNH NGHĨA DATACLASS ---
@dataclass
class MaxPermeanceOutput:
    """
    Kết quả tìm kiếm độ từ thẩm cực đại.
    """
    mu_r_max: float    # Giá trị mu_r lớn nhất
    B_at_max: float    # Giá trị B tại điểm cực đại [T]
    H_at_max: float    # Giá trị H tại điểm cực đại [A/m]

# --- 2. HÀM ĐÃ SỬA ĐỔI ---
def find_maximum_permeance(material_database, n_points=5000) -> MaxPermeanceOutput:
    """
    Tìm độ từ thẩm tương đối cực đại (mu_r) của sắt trong material_database.
    Trả về object MaxPermeanceOutput chứa (mu_max, B_max, H_max).
    """
    # Lấy dữ liệu BH từ Iron
    B_TABLE = material_database.iron.B_H_curve["B_data"]
    H_TABLE = material_database.iron.B_H_curve["H_data"]

    # Nội suy H(B) để có độ mịn cao hơn bảng dữ liệu gốc
    H_interpolator = interp1d(
        B_TABLE, H_TABLE,
        kind="cubic",
        fill_value="extrapolate"
    )

    # Quét lưới B (Tránh điểm 0 tuyệt đối để không chia cho 0)
    # Bắt đầu từ một giá trị rất nhỏ thay vì 0
    B_grid = np.linspace(max(1e-6, B_TABLE[0]), B_TABLE[-1], n_points)
    H_grid = H_interpolator(B_grid)

    # Tính mu_r(B) = B / (μ0 * H)
    # Sử dụng np.divide với where để an toàn, gán NaN nếu H=0
    mu_r_grid = np.divide(B_grid, MU0 * H_grid, out=np.full_like(B_grid, np.nan), where=H_grid != 0)

    # Tìm vị trí (index) có giá trị lớn nhất
    idx_max = np.nanargmax(mu_r_grid)

    # Trích xuất kết quả
    mu_r_max = mu_r_grid[idx_max]
    B_at_max = B_grid[idx_max]
    H_at_max = H_grid[idx_max]

    return MaxPermeanceOutput(
        mu_r_max=float(mu_r_max),
        B_at_max=float(B_at_max),
        H_at_max=float(H_at_max)
    )