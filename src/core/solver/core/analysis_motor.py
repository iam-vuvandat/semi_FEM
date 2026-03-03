import numpy as np
import math 
from tqdm import tqdm
from src.core.solver.utils.periodic_derivative import periodic_derivative
from src.core.solver.utils.duplicate_data import duplicate_data

pi = math.pi

def analysis_motor(motor, callback = None):
    
    def setup_callback(msg, *args):
        if callback:
            callback(msg)

    motor.state_manager.require(motor, "calculation_data", callback=setup_callback)

    calculation_data = motor.calculation_data
    max_relative_residual = calculation_data.max_relative_residual
    max_iteration = calculation_data.max_iteration
    material_relax = calculation_data.material_relax
    solve_cogging = calculation_data.solve_cogging
    n_point = calculation_data.n_point
    solve_only_1_step = calculation_data.solve_only_1_step
    get_geometric_error = calculation_data.get_geometric_error
    debug = calculation_data.debug

    epsilon = 1e-12
    symmetry_factor = motor.mechanical.symmetry_factor
    symmetry_angle = 2*pi / symmetry_factor
    cogging_angle = motor.mechanical.cogging_period_mech
    angle_factor = int(symmetry_angle // cogging_angle) 
    delta_theta  = cogging_angle / (n_point)
    minimum_theta_cell = int(math.ceil((symmetry_angle / delta_theta) - epsilon))

    if motor.adaptive_mesh_data.n_theta != minimum_theta_cell:
        motor.adaptive_mesh_data.n_theta = minimum_theta_cell
        motor.state_manager.just_changed("mesh")

    motor.state_manager.require(motor, "mesh", callback=setup_callback)
    motor.state_manager.require(motor, "reluctance_network", callback=setup_callback)

    if get_geometric_error:
        motor.reluctance_network.get_geometric_error()
    
    motor.state_manager.require(motor, "drive", callback=setup_callback)

    phase_number = motor.winding_data.phase
    flux_linkage = np.zeros((phase_number + 1, n_point))
    cogging = np.zeros((2, n_point))
    mst_data = np.zeros((5, n_point))
    
    # 1. Cogging Torque Analysis (No Excitation)
    if solve_cogging and not solve_only_1_step:
        motor.drive.apply_winding_excitation(excitation = False)
        for i in tqdm(range(n_point), desc="Solving Cogging", disable=not debug):
            motor.reluctance_network.solve(max_relative_residual = max_relative_residual,
                                        max_iteration = max_iteration,
                                        material_relax = material_relax, 
                                        damping_factor = 1.0,   
                                        debug = debug)
            
            cogging[0:2, i] = motor.maxwell_stress_tensor().mst_result[3:5]
            motor.rotate_rotor(n_step=1)
        
        # Reset rotor to position 0 after cogging analysis
        motor.rotate_rotor(n_step = -n_point)

    # 2. Standard Analysis (With Excitation)
    motor.drive.apply_winding_excitation(excitation = True)
    loop_steps_standard = 1 if solve_only_1_step else n_point
    
    for i in tqdm(range(loop_steps_standard), desc="Solving Standard", disable=not debug):
        if callback:
            callback(f"Solving Standard step {i+1}/{loop_steps_standard}")

        motor.reluctance_network.solve(max_relative_residual = max_relative_residual,
                                    max_iteration = max_iteration,
                                    material_relax = material_relax, 
                                    damping_factor = 1.0,   
                                    debug = debug)
        
        motor.reluctance_network.add_elements_lite()
        flux_linkage[:, i] = motor.reluctance_network.get_flux_linkage().flux_linkage[:, 0]
        mst_data[:, i] = motor.maxwell_stress_tensor().mst_result

        if not solve_only_1_step:
            motor.rotate_rotor(n_step = angle_factor)

    if solve_only_1_step:
        if callback: callback("Single step analysis completed")
        return None

    # Post-processing
    if callback: callback("Post-processing data...")
    motor.require("record")
    shaft_speed = motor.mechanical.shaft_speed * (pi/30)
    
    if motor.mesh.adaptive_mesh_data.use_symmetry_factor:
        flux_linkage *= symmetry_factor
        mst_data *= symmetry_factor
        cogging *= symmetry_factor

    back_emf = periodic_derivative(data=flux_linkage, half_open_interval=True).derivative * shaft_speed
    cogging_duplicated = duplicate_data(data = cogging, half_open_interval=True).duplicated_data

    motor.record.flux_linkage = flux_linkage.copy()
    motor.record.back_emf = back_emf.copy()
    motor.record.mst_data = mst_data.copy()
    motor.record.cogging = cogging_duplicated.copy()

    if callback: callback("Analysis Completed")
    return None