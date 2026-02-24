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
        return self.geometry_data.rotor.pole_number / 2

    @property
    def phase_number(self):
        return self.winding_data.phase

    @property
    def theta_e(self):
        return self.mechanical.current_position * self.pole_pairs

    def set_control(self, i_rms, phase_advanced):
        self.i_rms = i_rms
        self.phase_advanced = phase_advanced
        
        i_peak = i_rms * math.sqrt(2)
        beta_rad = math.radians(phase_advanced)
        
        self.id = -i_peak * math.sin(beta_rad)
        self.iq = i_peak * math.cos(beta_rad)

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
        self.reluctance_network.update_reluctance_network(winding_current = currents)

if __name__ == "__main__":
    class Mock:
        pass

    motor = Mock()
    motor.mechanical = Mock()
    motor.mechanical.current_position = 0.0
    
    motor.winding_data = Mock()
    motor.winding_data.phase = 3
    
    motor.geometry_data = Mock()
    motor.geometry_data.rotor = Mock()
    motor.geometry_data.rotor.pole_number = 4
    
    motor.reluctance_network = Mock()
    def mock_update(winding_current=None):
        motor.reluctance_network.last_current = winding_current
    motor.reluctance_network.update_reluctance_network = mock_update
    
    drive = Drive(motor)
    drive.set_control(i_rms=5, phase_advanced=0)
    
    positions = np.linspace(0, 2 * pi / drive.pole_pairs, 500)
    currents_history = []
    
    for pos in positions:
        motor.mechanical.current_position = pos
        drive.apply_winding_excitation()
        currents_history.append(motor.reluctance_network.last_current)
    
    currents_history = np.array(currents_history)
    
    plt.figure(figsize=(10, 6))
    plt.plot(np.degrees(positions), currents_history)
    plt.xlabel("Mechanical Position (Degree)")
    plt.ylabel("Phase Currents (A)")
    plt.title(f"{int(drive.phase_number)}-Phase Current Simulation (Numpy Output)")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend([f"Phase {k}" for k in range(int(drive.phase_number))])
    plt.tight_layout()
    plt.show()