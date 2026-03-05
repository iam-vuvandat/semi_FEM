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
        
        self.i_rms = self.drive_data.i_rms
        self.phase_advanced = self.drive_data.phase_advanced
        
        self._sync_dq_components()

    def _sync_dq_components(self):
        """Tính toán id, iq dựa trên i_rms và phase_advanced hiện tại."""
        i_peak = self.i_rms * math.sqrt(2)
        beta_rad = math.radians(self.phase_advanced)
        # id am de tao tu truong nguoc chieu (flux weakening) neu beta > 0
        self.id = -i_peak * math.sin(beta_rad)
        self.iq = i_peak * math.cos(beta_rad)

    @property
    def pole_pairs(self):
        return int(self.geometry_data.rotor.pole_number // 2)

    @property
    def phase_number(self):
        return self.winding_data.phase

    @property
    def theta_e(self):
        # Vi tri co hoc da la Radian (theo log), theta_e cung se la Radian
        return self.mechanical.current_position * self.pole_pairs

    @property
    def current_function(self):
        """Hien thi ham dong dien phai khop voi calculate_n_phase_currents."""
        functions = []
        i_peak = self.i_rms * math.sqrt(2)
        speed_rpm = getattr(self.mechanical, 'speed_rpm', 3000)
        omega_e = (speed_rpm * 2 * pi / 60) * self.pole_pairs
        beta_rad = math.radians(self.phase_advanced)
        
        for k in range(int(self.phase_number)):
            angle_shift = (2 * pi * k) / self.phase_number
            # Su dung ham cos de phan anh dung phep bien doi Park nguoc
            # Bo pi/2 de khong bi lech pha voi bo giai
            phi = beta_rad + angle_shift 
            func_str = f"{round(i_peak, 4)} * cos({round(omega_e, 4)} * Time + {round(phi, 4)})A"
            functions.append(func_str)
        return functions

    def set_control(self, i_rms, phase_advanced):
        self.i_rms = i_rms
        self.phase_advanced = phase_advanced
        self.drive_data.i_rms = i_rms
        self.drive_data.phase_advanced = phase_advanced
        self._sync_dq_components()

    def calculate_n_phase_currents(self):
        """Phep bien doi Park nguoc chuan cho PMSM."""
        theta_e = self.theta_e
        # Phep tinh Alpha-Beta tu DQ
        i_alpha = self.id * math.cos(theta_e) - self.iq * math.sin(theta_e)
        i_beta  = self.id * math.sin(theta_e) + self.iq * math.cos(theta_e)
        
        current_phases = []
        for k in range(int(self.phase_number)):
            angle_shift = (2 * pi * k) / self.phase_number
            # Phep bien doi Clarke nguoc (Alpha-Beta -> ABC)
            i_k = i_alpha * math.cos(angle_shift) + i_beta * math.sin(angle_shift)
            current_phases.append(i_k)
        return np.array(current_phases)

    def apply_winding_excitation(self, excitation = True):
        currents = self.calculate_n_phase_currents()
        if excitation is False:
            currents *= 0.0

        self.reluctance_network.update_reluctance_network(
            winding_current = currents, 
            update_for_winding_current = True
        )
if __name__ == "__main__":
    # --- 1. GIA LAP DOI TUONG MOTOR ---
    class MockData: pass
    
    motor = MockData()
    motor.mechanical = MockData()
    motor.mechanical.current_position = 0.0 # Radian
    motor.mechanical.speed_rpm = 3000
    
    motor.winding_data = MockData()
    motor.winding_data.phase = 3
    
    motor.geometry_data = MockData()
    motor.geometry_data.rotor = MockData()
    motor.geometry_data.rotor.pole_number = 8 # 4 cap cuc
    
    motor.drive_data = MockData()
    motor.drive_data.i_rms = 10.0 # 10A RMS
    motor.drive_data.phase_advanced = 30.0 # 30 do (Electric Degree)
    
    motor.reluctance_network = MockData()
    # Gia lap method de khong bi loi khi goi apply_winding_excitation
    def mock_update(winding_current, update_for_winding_current):
        pass
    motor.reluctance_network.update_reluctance_network = mock_update

    # --- 2. KHOI TAO DRIVE ---
    drive = Drive(motor)
    
    # --- 3. MO PHONG QUATRINH QUAY (1 CHU KY DIEN) ---
    steps = 100
    # 1 chu ky dien = 2*pi / p (mechanical rad)
    p = drive.pole_pairs
    positions = np.linspace(0, (2 * pi) / p, steps)
    
    results = []
    
    print(f"[INFO] Testing Drive with {drive.phase_number} phases...")
    print(f"[INFO] Current Functions: {drive.current_function}")

    for pos in positions:
        drive.mechanical.current_position = pos
        currents = drive.calculate_n_phase_currents()
        results.append(currents)
    
    results = np.array(results)

    # --- 4. VE DO THI KIEM TRA ---
    plt.figure(figsize=(10, 5))
    for i in range(int(drive.phase_number)):
        plt.plot(np.degrees(positions * p), results[:, i], label=f'Phase {i+1}')
    
    plt.title(f"Multi-phase Currents (i_rms={drive.i_rms}A, beta={drive.phase_advanced}deg)")
    plt.xlabel("Electrical Angle (Degrees)")
    plt.ylabel("Current (A)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    plt.show()

    # --- 5. KIEM TRA TINH CAN BANG (Sum of currents = 0) ---
    sum_currents = np.sum(results, axis=1)
    if np.all(np.abs(sum_currents) < 1e-10):
        print("\033[92m[PASS] He thong dong dien can bang (Tong = 0)\033[0m")
    else:
        print("\033[91m[FAIL] He thong khong can bang! Kiem tra lai phep bien doi Clarke.\033[0m")