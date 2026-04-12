import numpy as np 

from src.core.motor_type.utils.for_create_geometry.find_symmetry_factor import find_symmetry_factor
from src.core.motor_type.utils.for_create_geometry.find_cogging_period import find_cogging_period

class Mechanical:
    def __init__(self, motor):
        self.motor = motor
        self.geometry_data = motor.geometry_data
        self.mechanical_data = motor.mechanical_data
        self.shaft_speed = self.mechanical_data.shaft_speed
        self.current_position = 0.0
        self.step_rotated = 0
        self.cogging_period_mech = find_cogging_period(geometry_data = self.geometry_data).period_mech
        self.symmetry_factor = find_symmetry_factor(geometry_data= self.geometry_data).symmetry_factor
        self.slot_arc = (2*np.pi) / self.geometry_data.stator.slot_number
        self.pole_arc = (2*np.pi) / self.geometry_data.rotor.pole_number

    def reset_motor_position(self):
        motor = self.motor
        step_rotated = int(self.step_rotated)
        if step_rotated !=0:
            motor.rotate_rotor(n_step = - step_rotated)
            print(f"rotated {-step_rotated} step, current_position: {motor.mechanical.current_position}")
                