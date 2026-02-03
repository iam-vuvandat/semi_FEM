import numpy as np

class Output:
    """
    Container class to store the calculated winding matrix.
    """
    def __init__(self, winding_matrix = None, slot_matrix = None, mmf_offset = None):
        self.winding_matrix = winding_matrix
        self.slot_matrix = slot_matrix
        self.mmf_offset = mmf_offset

def init_winding(motor):
    """
    Generates the winding layout matrix based on the motor's configuration.
    """

    
    stator_params = motor.geometry_data.stator
    winding_params = motor.winding_data

    winding_type = winding_params.winding_type
    phase = winding_params.phase
    turns = winding_params.turns
    slot_number = stator_params.slot_number

    slot_matrix = np.zeros((int(slot_number), int(phase)))
    mmf_offset = 0.0

    if winding_type == "concentrated":
        winding_matrix = np.zeros((int(slot_number), int(phase)))
        
        for i in range(int(slot_number)):
            j = i % int(phase)
            winding_matrix[i, j] = turns
    

    return Output(winding_matrix=winding_matrix,slot_matrix = slot_matrix, mmf_offset= mmf_offset)