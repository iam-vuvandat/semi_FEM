import pickle
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_mbgrn_to_parameter(motor_io, path=None):
    """
    Reads the .mbgrn file and populates the motor_io.motor_parameter attribute.
    """
    # Adjust recursion depth to handle complex serialized data structures
    sys.setrecursionlimit(1000)
    
    # Resolve the absolute path using the motor_io internal logic
    full_path = motor_io._resolve_full_path(path)
    
    # Check if the target file exists before attempting to load
    if not full_path.exists():
        logger.error(f"Load failed: File not found at {full_path}")
        return None

    # Open and deserialize the MotorIO object from the binary file
    with open(full_path, "rb") as f:
        loaded_io = pickle.load(f)
    
    # Transfer the loaded motor_parameter to the current motor_io instance
    if hasattr(loaded_io, 'motor_parameter'):
        motor_io.motor_parameter = loaded_io.motor_parameter
        
        # Notify the user of successful parameter retrieval in green
        print(f"\033[92mSuccessfully loaded parameters from: {full_path}\033[0m")
        return full_path
    
    return None