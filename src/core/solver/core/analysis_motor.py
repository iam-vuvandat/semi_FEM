import numpy as np
import math 
from tqdm import tqdm

from src.core.solver.utils.periodic_derivative import periodic_derivative
from src.core.solver.utils.duplicate_data import duplicate_data

pi = math.pi

def analysis_motor(motor, callback = None):
    
    # Hàm bọc để bảo vệ callback, chỉ lấy tham số đầu tiên (chuỗi văn bản)
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
    mst_data = np.zeros((5, n_point))
    
    n_step_cogging = 1 
    n_step_standard = angle_factor
    cogging_shifted = 0

    loop_steps = 1 if solve_only_1_step else minimum_theta_cell
    for i in tqdm(range(loop_steps), disable=not debug):
        if callback:
            callback(f"Solving step {i+1}/{loop_steps}")

        if solve_cogging:
            is_cogging_point = (i < n_point)
        else:
            is_cogging_point = False

        is_standard_point = (i % n_step_standard == 0)

        if is_cogging_point or is_standard_point:
            motor.drive.apply_winding_excitation()
            motor.reluctance_network.solve(max_relative_residual = max_relative_residual,
                                            max_iteration = max_iteration,
                                            material_relax = material_relax, 
                                            damping_factor = 1.0,   
                                            debug = debug)
            
            if is_cogging_point:
                mst_data[:, i] = motor.maxwell_stress_tensor().mst_result

            if is_standard_point:
                motor.reluctance_network.add_elements_lite()
                index_standard = i // n_step_standard
                if index_standard < n_point:
                    flux_linkage[:, index_standard] = motor.reluctance_network.get_flux_linkage().flux_linkage[:, 0]
                cogging_shifted = 0

        if is_cogging_point:
            motor.rotate_rotor(n_step=n_step_cogging)
            cogging_shifted += n_step_cogging
        else:
            if is_standard_point:
                jump_step = int(n_step_standard - cogging_shifted)
                motor.rotate_rotor(n_step=jump_step)
                cogging_shifted = 0

    if solve_only_1_step:
        if callback: callback("Single step analysis completed")
        return None

    if callback: callback("Post-processing data...")

    motor.require("record")
    motor.record.flux_linkage = flux_linkage.copy()
    shaft_speed = motor.mechanical.shaft_speed * (pi/30)
    back_emf = periodic_derivative(data=flux_linkage, half_open_interval=True).derivative * shaft_speed 
    if motor.mesh.adaptive_mesh_data.use_symmetry_factor:
        back_emf = back_emf * motor.mechanical.symmetry_factor

    motor.record.back_emf = back_emf.copy()
    mst_data = duplicate_data(data=mst_data, half_open_interval=True).duplicated_data
    motor.record.mst_data = mst_data.copy()

    if callback: callback("Analysis Completed")
    return None


    