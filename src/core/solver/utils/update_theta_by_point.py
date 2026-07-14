import math

def update_theta_by_point(motor):
    motor.require("calculation_data")
    n_point = motor.calculation_data.general_options.n_point
    
    pi = math.pi
    symmetry_factor = motor.mechanical.symmetry_factor
    symmetry_angle = 2 * pi / symmetry_factor
    
    cogging_angle = motor.mechanical.cogging_period_mech
    
    epsilon = 1e-12
    delta_theta = cogging_angle / n_point
    minimum_theta_cell = int(math.ceil((symmetry_angle / delta_theta) - epsilon))
    
    if motor.adaptive_mesh_data.n_theta != minimum_theta_cell:
        print("\033[94mIn function update_theta_by_point: \033[0m")
        print("\033[94m{\033[0m")
        
        motor.adaptive_mesh_data.n_theta = minimum_theta_cell
        motor.just_changed("mesh")
        
        print(f"\033[94mn theta cell has been updated to [{minimum_theta_cell}]\033[0m")
        print("\033[94m}\033[0m")
        print("\033[94m\033[0m")
        
    return motor