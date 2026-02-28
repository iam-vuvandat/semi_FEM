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
        self.drive_data = motor.drive_data
        
        # Nạp hằng số từ drive_data
        self.i_rms = self.drive_data.i_rms
        self.phase_advanced = self.drive_data.phase_advanced
        
        # TỰ ĐỘNG tính toán id, iq ngay khi khởi tạo để tránh dòng điện = 0
        self._sync_dq_components()

    def _sync_dq_components(self):
        """Tính toán id, iq dựa trên i_rms và phase_advanced hiện tại."""
        i_peak = self.i_rms * math.sqrt(2)
        beta_rad = math.radians(self.phase_advanced)
        self.id = -i_peak * math.sin(beta_rad)
        self.iq = i_peak * math.cos(beta_rad)

    @property
    def pole_pairs(self):
        """Số đôi cực từ (p)."""
        return int(self.geometry_data.rotor.pole_number // 2)

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
        functions = []
        i_peak = self.i_rms * math.sqrt(2)
        speed_rpm = getattr(self.mechanical, 'speed_rpm', 3000)
        omega_e = (speed_rpm * 2 * pi / 60) * self.pole_pairs
        beta_rad = math.radians(self.phase_advanced)
        
        for k in range(int(self.phase_number)):
            angle_shift = (2 * pi * k) / self.phase_number
            phi = beta_rad + angle_shift + (pi / 2)
            func_str = f"{round(i_peak, 4)} * sin({round(omega_e, 4)} * Time + {round(phi, 4)})A"
            functions.append(func_str)
        return functions

    def set_control(self, i_rms, phase_advanced):
        """Thiết lập thông số và đồng bộ hóa vào drive_data."""
        self.i_rms = i_rms
        self.phase_advanced = phase_advanced
        
        # Đồng bộ ngược lại drive_data để lưu trữ bền vững
        self.drive_data.i_rms = i_rms
        self.drive_data.phase_advanced = phase_advanced
        
        self._sync_dq_components()

    def calculate_n_phase_currents(self):
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
        currents = self.calculate_n_phase_currents()
        self.reluctance_network.update_reluctance_network(
            winding_current = currents, 
            update_for_winding_current = True
        )