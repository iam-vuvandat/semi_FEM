import numpy as np 
from src.core.motor_type.utils.for_create_geometry.find_symmetry_factor import find_symmetry_factor
from src.core.motor_type.utils.for_create_geometry.find_cogging_period import find_cogging_period

class Mechanical:
    def __init__(self,motor):
        self.motor = motor
        self.shaft_speed = motor.mechanical_data.shaft_speed
        self.current_position = 0.0

        self.symmetry_factor = find_symmetry_factor(motor=self.motor).symmetry_factor
        self.cogging_period_mech = find_cogging_period(slots = self.motor.geometry_data.stator.slot_number,
                                                       poles = self.motor.geometry_data.rotor.pole_number).period_mech
        
