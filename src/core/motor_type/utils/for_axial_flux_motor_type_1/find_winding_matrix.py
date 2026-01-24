import numpy as np

class Output:
    """
    Container class to store the calculated winding matrix.
    """
    def __init__(self, winding_matrix = None):
        self.winding_matrix = winding_matrix

def find_winding_matrix(motor):
    """
    Generates the winding layout matrix based on the motor's configuration.
    Redirects variable access to the new nested Container structures.
    """
    # Accessing parameters through the refactored structure
    stator_params = motor.geometry_data.stator
    winding_params = motor.winding_data

    # Mapping to long-form variable names as per the new object structure
    winding_type = winding_params.winding_type
    phase_count  = winding_params.phase_number
    turns_per_coil = winding_params.turns_number
    slot_count   = stator_params.slot_number

    # Logic for concentrated winding remains strictly identical to original code
    if winding_type == "concentrated":
        # Initialize zero matrix with dimensions (Slots x Phases)
        winding_matrix = np.zeros((int(slot_count), int(phase_count)))
        
        for i in range(int(slot_count)):
            # Simple alternating phase assignment for concentrated layout
            j = i % int(phase_count)
            winding_matrix[i, j] = turns_per_coil

    return Output(winding_matrix=winding_matrix)