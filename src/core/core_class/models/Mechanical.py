import numpy as np 
import math

from src.core.motor_type.utils.for_create_geometry.find_symmetry_factor import find_symmetry_factor
from src.core.motor_type.utils.for_create_geometry.find_cogging_period import find_cogging_period

class Mechanical:
    def __init__(self, motor):
        self.motor = motor
        self.geometry_data = motor.geometry_data
        self.mechanical_data = motor.mechanical_data
        self.shaft_speed = self.mechanical_data.shaft_speed
        self.omega = (self.shaft_speed * 2 * np.pi) / 60

        self.current_position = 0.0
        self.step_rotated = 0
        self.cogging_period_mech = find_cogging_period(geometry_data = self.geometry_data).period_mech
        
        self.symmetry_factor = find_symmetry_factor(geometry_data= self.geometry_data).symmetry_factor
        self.slot_arc = (2*np.pi) / self.geometry_data.stator.slot_number
        self.pole_arc = (2*np.pi) / self.geometry_data.rotor.pole_number

        print(f"\033[94mIn function Mechanical.__init__:\033[0m")
        print("\033[94m{\033[0m")
        print(f"\033[94m    cogging_period_mech: {self.cogging_period_mech} rad ({math.degrees(self.cogging_period_mech)} deg)\033[0m")
        print(f"\033[94m    slot_arc: {self.slot_arc} rad ({math.degrees(self.slot_arc)} deg)\033[0m")
        print(f"\033[94m    pole_arc: {self.pole_arc} rad ({math.degrees(self.pole_arc)} deg)\033[0m")
        print(f"\033[94m    symmetry_factor: {self.symmetry_factor}\033[0m")
        print("\033[94m}\033[0m\n")
        
    
    def reset_motor_position(self):
        motor = self.motor
        step_rotated = int(self.step_rotated)
        if step_rotated != 0:
            print(f"\033[94mIn function Mechanical.reset_motor_position:\033[0m")
            print("\033[94m{\033[0m")
            motor.rotate_rotor(n_step = - step_rotated)
            print(f"\033[94m    Success: rotated {-step_rotated} step, current_position: {motor.mechanical.current_position}\033[0m")
            print("\033[94m}\033[0m\n")