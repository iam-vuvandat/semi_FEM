import paths 
import numpy as np
import math 
from tqdm import tqdm

pi = math.pi
from src.core.solver.utils.periodic_derivative import periodic_derivative
from src.core.solver.utils.duplicate_data import duplicate_data

def analysis_motor(motor, callback = None):
    motor.require("calculation_data")
    calculation_data = motor.calculation_data
    max_relative_residual = calculation_data.max_relative_residual
    max_iteration = calculation_data.max_iteration
    material_relax = calculation_data.material_relax
    solve_cogging = calculation_data.solve_cogging
    n_point = calculation_data.n_point
    debug = calculation_data.debug
    phases = motor.winding_data.phase 

    epsilon = 1e-12
    symmetry_factor = motor.mechanical.symmetry_factor
    symmetry_angle = 2*pi / symmetry_factor
    cogging_angle = motor.mechanical.cogging_period_mech
    angle_factor = int(symmetry_angle // cogging_angle) 
    delta_theta  = cogging_angle / (n_point)
    minimum_theta_cell = int(math.ceil((symmetry_angle / delta_theta) - epsilon))

    def scaled_callback(msg, sub_progress):
        if callback:
            total_progress = int(sub_progress * 0.15)
            callback(msg, total_progress)

    
    if motor.adaptive_mesh_data.n_theta ==  minimum_theta_cell:
        pass
    
    else:
        motor.adaptive_mesh_data.n_theta = minimum_theta_cell 
        motor.just_changed("mesh")

    motor.require("drive")

    
    phase_number = motor.winding_data.phase
    flux_linkage = np.zeros((phase_number + 3, n_point))
    cogging = np.zeros((2, n_point))
    mst_data = np.zeros((5, n_point))
    current = np.zeros((3 + phases, n_point))
    
    n_step_cogging = 1 
    n_step_standard = angle_factor
    cogging_shifted = 0

    for i in tqdm(range(minimum_theta_cell), disable=not debug):
        if callback:
            progress_val = int(15 + (i / minimum_theta_cell) * 75)
            callback(f"Solving FVM step {i+1}/{minimum_theta_cell}", progress_val)

        if solve_cogging:
            is_cogging_point = (i < n_point)
        else:
            is_cogging_point = False

        is_standard_point = (i % n_step_standard == 0)

        if is_cogging_point or is_standard_point:
            
            if is_cogging_point:
                motor.drive.apply_winding_excitation(excitation = False)
                motor.reluctance_network.solve(
                                            max_relative_residual = max_relative_residual,
                                            max_iteration = max_iteration,
                                            material_relax = material_relax, 
                                            damping_factor = 1.0,   
                                            debug = debug)
                
                cogging[:, i] = motor.maxwell_stress_tensor().mst_result[3:5]

            if is_standard_point:
                motor.drive.apply_winding_excitation(excitation = True)
                motor.reluctance_network.solve(
                                            max_relative_residual = max_relative_residual,
                                            max_iteration = max_iteration,
                                            material_relax = material_relax, 
                                            damping_factor = 1.0,   
                                            debug = debug)
                
                motor.reluctance_network.add_elements_lite()
                index_standard = i // n_step_standard
                if index_standard < n_point:
                    flux_linkage[:, index_standard] = motor.reluctance_network.get_flux_linkage().flux_linkage[:, 0]
                    mst_data[:,index_standard] = motor.maxwell_stress_tensor().mst_result[:]
                    current[:,index_standard] = motor.drive.debug_current()[:]

                cogging_shifted = 0

        if is_cogging_point:
            motor.rotate_rotor(n_step=n_step_cogging)
            cogging_shifted += n_step_cogging
        else:
            if is_standard_point:
                jump_step = int(n_step_standard - cogging_shifted)
                motor.rotate_rotor(n_step=jump_step)
                cogging_shifted = 0

    if callback: callback("Post-processing data", 95)
    

    # symmetry:
    use_symmetry = motor.mesh.periodic_boundary
    if use_symmetry:
        flux_linkage[:-1] *= symmetry_factor
        mst_data[:-1] *= symmetry_factor
        cogging[:-1] *= symmetry_factor


    # handle data
    shaft_speed = motor.mechanical.shaft_speed * (pi/30)
    back_emf = periodic_derivative(data=flux_linkage[2:], half_open_interval=True).derivative * shaft_speed 
    
    mst_data = duplicate_data(data=mst_data, half_open_interval=True).duplicated_data
    cogging = duplicate_data(data=cogging, half_open_interval=True).duplicated_data
    

    # Save

    motor.record.flux_linkage = flux_linkage.copy()
    motor.record.back_emf = back_emf.copy()
    motor.record.mst_data = mst_data.copy()
    motor.record.cogging = cogging.copy()
    motor.record.currents = current.copy()

    if callback: callback("Analysis Completed", 100)
    return None