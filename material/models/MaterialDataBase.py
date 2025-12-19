import math
import numpy as np
from scipy.interpolate import PchipInterpolator, UnivariateSpline

PI = math.pi

class Air:
    def __init__(self, name="default"):
        self.name = name
        self.relative_permeance = 1.

class Magnet:
    def __init__(self, name: str):
        self.name = name
        if name == "N30UH":
            self.relative_permeance = 1.05
            self.coercivity = 852000.0
        else:
            raise ValueError(f"Magnet '{name}' not found")

class Iron:
    def __init__(self, name: str):
        self.name = name
        if name == "M350-50A":
            self.B_H_curve = {
                "B_data": np.array([
                    0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
                    1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9,
                    1.956, 2.1, 2.2, 2.2701, 2.4
                ]),
                "H_data": np.array([
                    0.0, 34.8, 46.0, 53.7, 60.6, 67.4, 74.6, 82.6, 91.8, 103.0,
                    119.0, 141.0, 178.0, 250.0, 455.0, 1180.0, 3020.0, 6100.0,
                    10700.0, 25000.0, 35000.0, 75000.0, 115000.0, 150000.0, 229580.0
                ])
            }
        else:
            raise ValueError(f"Iron '{name}' not found")
        
        self.smooth_BH_curve()

    def smooth_BH_curve(self, num_points=3000):
        mu_0 = 4 * PI * 1e-7
        
        B_raw = self.B_H_curve["B_data"]
        H_raw = self.B_H_curve["H_data"]
        
        # --- BƯỚC 1: TÍNH TOÁN MU_R CƠ BẢN ---
        with np.errstate(divide='ignore', invalid='ignore'):
            mu_r_raw = B_raw / (mu_0 * H_raw)
        
        # Xử lý điểm 0 (L'Hopital - xấp xỉ tuyến tính đoạn đầu)
        initial_mu = (B_raw[1] / H_raw[1]) / mu_0
        mu_r_raw[0] = initial_mu

        # --- BƯỚC 2: TẠO ĐƯỜNG CONG DẪN ĐƯỜNG (GUIDE CURVE) ---
        # Dùng Pchip để nội suy ra dữ liệu thô nhưng dày đặc
        pchip_fit = PchipInterpolator(B_raw, mu_r_raw)
        
        # --- BƯỚC 3: GIẢM SỐ ĐIỂM (DOWNSAMPLING) ---
        # GIẢM SỐ ĐIỂM: Chỉ dùng 30 điểm để định hình đường cong.
        # 30 điểm là đủ để mô tả hình quả chuông (Bell shape) của Mu_r
        # mà không đủ "độ phân giải" để sao chép các nhiễu đo lường.
        num_control_points = 30 
        B_coarse = np.linspace(B_raw.min(), B_raw.max(), num_control_points)
        mu_coarse = pchip_fit(B_coarse)
        
        # --- BƯỚC 4: CHUẨN BỊ DỮ LIỆU LOGARIT ---
        # Chuyển sang miền Log để làm phẳng đỉnh và tuyến tính hóa các sườn dốc
        log_mu_coarse = np.log(mu_coarse)

        # Phản chiếu dữ liệu (Mirroring) để đảm bảo đạo hàm tại 0 bằng 0 tuyệt đối
        B_mirror = np.concatenate((-B_coarse[1:][::-1], B_coarse))
        log_mu_mirror = np.concatenate((log_mu_coarse[1:][::-1], log_mu_coarse))

        # --- BƯỚC 5: LÀM MƯỢT LẦN 2 (SPLINE FITTING) ---
        # Fit spline lên lưới thưa. 
        # s=0.01 là đủ nhẹ để làm trơn các gãy khúc nhỏ còn sót lại trên lưới thưa.
        spline_final = UnivariateSpline(B_mirror, log_mu_mirror, k=3, s=0.01)

        # --- BƯỚC 6: TÁI TẠO LƯỚI DÀY ĐẶC ---
        B_final = np.linspace(B_raw.min(), B_raw.max(), num_points)
        
        log_mu_final = spline_final(B_final)
        mu_r_final = np.exp(log_mu_final)
        
        # Đảm bảo điểm 0 phẳng (đạo hàm = 0)
        # Lấy giá trị spline tại 0 thay vì gán bằng điểm bên cạnh để chính xác hơn về mặt toán học
        mu_r_final[0] = np.exp(spline_final(0))

        # Tính lại H từ Mu_r đã làm mượt
        H_final = np.zeros_like(B_final)
        H_final[1:] = B_final[1:] / (mu_0 * mu_r_final[1:])
        H_final[0] = 0

        self.B_H_curve["B_data"] = B_final
        self.B_H_curve["H_data"] = H_final

class MaterialDataBase:
    def __init__(self, air="default", magnet_type="N30UH", iron_type="M350-50A"):
        self.air = Air(air)
        self.magnet = Magnet(magnet_type)
        self.iron = Iron(iron_type)