import numpy as np

class Output:
    def __init__(self, winding_matrix = None, slot_matrix = None):
        self.winding_matrix = winding_matrix
        self.slot_matrix    = slot_matrix

def init_winding(motor):
    stator = motor.geometry_data.stator
    rotor = motor.geometry_data.rotor

    slot_number = stator.slot_number
    pole_number = rotor.pole_number

    winding_matrix = None
    slot_matrix = None

    winding_data = motor.winding_data
    winding_type = winding_data.winding_type
    phase = winding_data.phase
    turns = winding_data.turns
    pole_throw = winding_data.pole_throw
    throw = winding_data.throw
    parallel_path = winding_data.parallel_path
    winding_layer = winding_layer
    offset = winding_data.offset

    return Output(winding_matrix= winding_matrix,
                  slot_matrix= slot_matrix)