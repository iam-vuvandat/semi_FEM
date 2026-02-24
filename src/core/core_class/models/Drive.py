import math
import matplotlib.pyplot as plt
import numpy as np

pi = math.pi

class Drive:
    def __init__(self, motor):
        self.mechanical = motor.mechanical
        self.winding_data = motor.winding_data
        self.geometry_data = motor.geometry_data
        self.reluctance_network = motor.reluctance_network
        
        self.i_rms = 0.0
        self.phase_advanced = 0.0
        self.id = 0.0
        self.iq = 0.0

    @property
    def pole_pairs(self):
        """Số đôi cực từ (p)."""
        return self.geometry_data.rotor.pole_number / 2

    @property
    def phase_number(self):
        """Số pha của dây quấn."""
        return self.winding_data.phase

    @property
    def theta_e(self):
        """Góc điện tức thời dựa trên vị trí cơ học."""
        return self.mechanical.current_position * self.pole_pairs

    @property
    def current_function(self):
        """
        Trả về danh sách các chuỗi biểu thức dòng điện tường minh cho Maxwell 3D.
        Dạng: I_peak * sin(omega_e * Time + phi)
        """
        functions = []
        i_peak = self.i_rms * math.sqrt(2)
        
        # Lấy tốc độ từ dự án semi_FEM (mặc định 3000 nếu chưa có)
        speed_rpm = getattr(self.mechanical, 'speed_rpm', 3000)
        # Tần số góc điện omega_e = (2*pi*n/60) * p
        omega_e = (speed_rpm * 2 * pi / 60) * self.pole_pairs
        
        # Góc tiến dòng (beta) quy đổi sang Radian
        beta_rad = math.radians(self.phase_advanced)
        
        for k in range(int(self.phase_number)):
            # Góc lệch pha hình học giữa các pha
            angle_shift = (2 * pi * k) / self.phase_number
            
            # Pha ban đầu tổng cộng (phi)
            # Cộng thêm pi/2 để đồng bộ logic id/iq (cos/sin) với hàm sin của Maxwell
            phi = beta_rad + angle_shift + (pi / 2)
            
            # Tạo chuỗi tường minh: Maxwell sẽ sử dụng biến nội tại 'Time'
            func_str = f"{round(i_peak, 4)} * sin({round(omega_e, 4)} * Time + {round(phi, 4)})"
            functions.append(func_str)
            
        return functions

    def set_control(self, i_rms, phase_advanced):
        """Thiết lập thông số điều khiển dòng điện."""
        self.i_rms = i_rms
        self.phase_advanced = phase_advanced
        
        i_peak = i_rms * math.sqrt(2)
        beta_rad = math.radians(phase_advanced)
        
        # Phân rã thành phần dòng điện d-q
        self.id = -i_peak * math.sin(beta_rad)
        self.iq = i_peak * math.cos(beta_rad)

    def calculate_n_phase_currents(self):
        """Tính toán giá trị dòng điện tức thời phục vụ Reluctance Network."""
        theta_e = self.theta_e
        
        i_alpha = self.id * math.cos(theta_e) - self.iq * math.sin(theta_e)
        i_beta  = self.id * math.sin(theta_e) + self.iq * math.cos(theta_e)
        
        current_phases = []
        for k in range(int(self.phase_number)):
            angle_shift = (2 * pi * k) / self.phase_number
            i_k = i_alpha * math.cos(angle_shift) + i_beta * math.sin(angle_shift)
            current_phases.append(i_k)
            
        return np.array(current_phases)

    def apply_winding_excitation(self):
        """Cập nhật dòng điện vào mạng điện trở từ (MBGRN)."""
        currents = self.calculate_n_phase_currents()
        self.reluctance_network.update_reluctance_network(winding_current = currents)

# --- Phần chạy thử nghiệm và In kết quả ---
if __name__ == "__main__":
    class Mock: pass

    # Giả lập dữ liệu motor từ semi_FEM
    motor = Mock()
    motor.mechanical = Mock()
    motor.mechanical.current_position = 0.0
    motor.mechanical.speed_rpm = 3000
    
    motor.winding_data = Mock()
    motor.winding_data.phase = 3
    
    motor.geometry_data = Mock()
    motor.geometry_data.rotor = Mock()
    motor.geometry_data.rotor.pole_number = 4 
    
    motor.reluctance_network = Mock()
    motor.reluctance_network.update_reluctance_network = lambda winding_current: None
    
    # Khởi tạo Drive
    drive = Drive(motor)
    drive.set_control(i_rms=5, phase_advanced= 0 ) # 5A RMS, góc tiến 15 độ
    
    # In kết quả tường minh dành cho Maxwell 3D
    print("--- Maxwell 3D Explicit Current Functions ---")
    for i, func in enumerate(drive.current_function):
        print(f"Phase {i}: {func}")
    print("---------------------------------------------\n")

    # Vẽ đồ thị kiểm tra dạng sóng tức thời
    positions = np.linspace(0, 2 * pi / drive.pole_pairs, 500)
    currents_history = []
    for pos in positions:
        motor.mechanical.current_position = pos
        currents_history.append(drive.calculate_n_phase_currents())
    
    plt.figure(figsize=(10, 5))
    plt.plot(np.degrees(positions), currents_history)
    plt.title("Instantaneous Phase Currents (Numpy Calculation)")
    plt.xlabel("Mechanical Position (Deg)")
    plt.ylabel("Current (A)")
    plt.grid(True)
    plt.legend([f"Phase {k}" for k in range(int(drive.phase_number))])
    plt.show()