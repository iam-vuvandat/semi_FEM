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
            # Phi duoc tinh toan de khop 100% voi phep bien doi Park/Clarke nguoc
            # Cong thuc: i_k = -i_peak * sin(omega_e*t - angle_shift + beta)
            phi = -angle_shift + beta_rad
            
            func_str = f"-{round(i_peak, 4)} * sin({round(omega_e, 4)} * Time + ({round(phi, 4)}))A"
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

    def apply_manual_winding_excitation(self, id, iq):
        self.id = id
        self.iq = iq
        currents = self.calculate_n_phase_currents()
        
        self.reluctance_network.update_reluctance_network(
            winding_current = currents, 
            update_for_winding_current = True
        )

    def debug_current(self):
        current_phases = self.calculate_n_phase_currents()
        # Cau truc mang: [id, iq, i1, i2, ..., iN, current_position]
        debug_array = np.concatenate(([self.id, self.iq], current_phases, [self.mechanical.current_position]))
        return debug_array
    