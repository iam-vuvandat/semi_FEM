from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1

def load_axial_flux_motor_type_1(motor_io):
    # Initialize a clean instance of the motor class
    motor = AxialFluxMotorType1()
    
    # Reference to the loaded parameters
    params = motor_io.motor_parameter
    
    # Manually restore design specifications and configuration
    motor.motor_type = params.motor_type
    motor.material_data = params.material_data
    motor.winding_data = params.winding_data
    motor.mechanical_data = params.mechanical_data
    motor.geometry_data = params.geometry_data
    motor.calculation_data = params.calculation_data
    motor.adaptive_mesh_data = params.adaptive_mesh_data
    motor.drive_data = params.drive_data
    motor.maxwell_export_option = params.maxwell_export_option
    motor.record = params.record
    
        
    return motor