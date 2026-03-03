import numpy as np
import math 
pi = math.pi 


class MaxwellIntegrationSurface:
    def __init__(self, 
                 elements = None, 
                 plane = "Ort",
                 direction = 1):
                 
        
        self.elements = elements
        self.plane = plane
        self.direction = direction
        self.elements_list = None
        self.mu_0 = 4 * math.pi * 1e-7

    def create_plane(self, layer = -1 , a1 = 0, a2 = None, b1 = 0 ,b2 = None):
        plane = self.plane
        if plane == "Ort":
            self.elements_list = self.elements[a1:a2,b1:b2,layer].flatten()

        elif plane == "Orz": 
            self.elements_list = self.elements[a1:a2,layer,b1:b2].flatten()

        else: # Otz
            self.elements_list = self.elements[layer,a1:a2,b1:b2].flatten()

    def integrate_maxwell_stress_tensor(self):
        """
        Tích phân Maxwell Stress Tensor (MST) - Hệ mét (SI Units).
        Trả về: np.array([Fr, Ft, Fz, Tz]) 
        (Đơn vị: Newton và Newton-meter)

        [0] : Radial force
        [1] : Tangential force
        [2] : Axial force
        [3] : Torque
        """
        if self.elements_list is None:
            return np.zeros(4)

        

        # Hàng 0: Nửa dưới/trong (direction -1), Hàng 1: Nửa trên/ngoài (direction 1)
        row_idx = 1 if self.direction == 1 else 0
        
        results = np.zeros(4) 

        for element in self.elements_list:
            # 1. Trích xuất dữ liệu từ Element (Sử dụng hệ mét trực tiếp)
            b_avg = element.flux_density_average
            b_mag_sq = b_avg[3]**2
            
            # Cánh tay đòn: r = (r_in + r_out) / 2
            r = (element.coordinate[0, 0] + element.coordinate[1, 0]) / 2
            
            sigma = np.zeros(3)
            
            # 2. Tính toán ứng suất dựa trên 3 loại mặt phẳng
            if self.plane == "Ort":
                # Mặt vành khăn (Pháp tuyến trục Z)
                ds = element.section_area[row_idx, 2] # Sz
                b_n = b_avg[2] * self.direction       # Bz * direction
                
                sigma[0] = (1.0 / self.mu_0) * (b_n * b_avg[0])
                sigma[1] = (1.0 / self.mu_0) * (b_n * b_avg[1])
                sigma[2] = (1.0 / self.mu_0) * (b_n * b_avg[2] - 0.5 * b_mag_sq * self.direction)

            elif self.plane == "Orz":
                # Mặt phẳng hướng tâm (Pháp tuyến trục Theta)
                ds = element.section_area[row_idx, 1] # St
                b_n = b_avg[1] * self.direction       # Bt * direction
                
                sigma[0] = (1.0 / self.mu_0) * (b_n * b_avg[0])
                sigma[1] = (1.0 / self.mu_0) * (b_n * b_avg[1] - 0.5 * b_mag_sq * self.direction)
                sigma[2] = (1.0 / self.mu_0) * (b_n * b_avg[2])

            elif self.plane == "Otz":
                # Mặt trụ biên (Pháp tuyến trục R)
                ds = element.section_area[row_idx, 0] # Sr
                b_n = b_avg[0] * self.direction       # Br * direction
                
                sigma[0] = (1.0 / self.mu_0) * (b_n * b_avg[0] - 0.5 * b_mag_sq * self.direction)
                sigma[1] = (1.0 / self.mu_0) * (b_n * b_avg[1])
                sigma[2] = (1.0 / self.mu_0) * (b_n * b_avg[2])

            # 3. Tổng hợp lực và mô-men (r x dFt)
            d_force = sigma * ds
            results[0:3] += d_force
            results[3]   += r * d_force[1] # Cánh tay đòn r nhân lực tiếp tuyến Ft

        return results