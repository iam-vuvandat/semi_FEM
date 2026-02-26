import numpy as np 

class Mechanical:
    def __init__(self,
                 shaft_speed = 3000,
                 current_position = 0.0):
        self.shaft_speed = float(shaft_speed)
        self.current_position = float(current_position)
        cogging_period_mech = 0.0
        symmetry_factor = 0.0
