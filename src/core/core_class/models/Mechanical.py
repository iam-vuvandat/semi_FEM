import numpy as np 
from src.core.motor_type.utils.for_create_geometry.find_symmetry_factor import find_symmetry_factor
from src.core.motor_type.utils.for_create_geometry.find_cogging_period import find_cogging_period

class Mechanical:
    def __init__(self,
                 motor):
        self.geometry_data = motor.geometry_data
        self.mechanical_data = motor.mechanical_data
        self.shaft_speed = self.mechanical_data.shaft_speed
        self.current_position = 0.0
        self.cogging_period_mech = find_cogging_period(geometry_data = self.geometry_data).period_mech
        self.symmetry_factor = find_symmetry_factor(geometry_data= self.geometry_data).symmetry_factor
        