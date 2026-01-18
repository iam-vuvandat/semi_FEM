import numpy as np

class Output:
    def __init__(self,winding_matrix = None):
        self.winding_matrix = winding_matrix

def find_winding_matrix(motor):
    winding_type = motor.winding_type
    phase = motor.phase
    turns = motor.turns
    slot_number = motor.slot_number

    if winding_type == "concentrated":
        winding_matrix = np.zeros((slot_number,phase))
        for i in range(int(slot_number)):
            j = i % int(phase)
            winding_matrix[i,j] = turns

    return Output(winding_matrix=winding_matrix)