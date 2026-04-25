import pickle
import sys
import logging
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_axial_flux_motor_type_1(motor_io, motor, path=None):
    # Adjust recursion depth for complex object structures
    sys.setrecursionlimit(1000) 
    
    # Resolve the destination path using the project root
    full_path = motor_io._resolve_full_path(path) 
    temp_path = full_path.with_suffix('.tmp')

    # Manually aggregate essential motor attributes into motor_parameter SimpleNamespace
    motor_io.motor_parameter.motor_type = motor.motor_type
    motor_io.motor_parameter.material_data = motor.material_data
    motor_io.motor_parameter.winding_data = motor.winding_data
    motor_io.motor_parameter.mechanical_data = motor.mechanical_data
    motor_io.motor_parameter.geometry_data = motor.geometry_data
    motor_io.motor_parameter.calculation_data = motor.calculation_data
    motor_io.motor_parameter.adaptive_mesh_data = motor.adaptive_mesh_data
    motor_io.motor_parameter.drive_data = motor.drive_data
    motor_io.motor_parameter.maxwell_export_option = motor.maxwell_export_option
    
    # Critical: Aggregate post-simulation data for restoration
    motor_io.motor_parameter.record = motor.record

    # Serialize the MotorIO object to a temporary file using the highest protocol
    with open(temp_path, "wb") as f:
        pickle.dump(motor_io, f, protocol=pickle.HIGHEST_PROTOCOL)

    # Atomic swap: move temporary file to final destination to prevent data corruption
    if temp_path.exists():
        shutil.move(str(temp_path), str(full_path))

    # Print success notification in green color
    # ANSI escape code: \033[92m is light green, \033[0m is reset
    print(f"\033[92mSuccessfully saved motor to: {full_path}\033[0m")

    # Return the absolute path as a string
    return str(full_path)