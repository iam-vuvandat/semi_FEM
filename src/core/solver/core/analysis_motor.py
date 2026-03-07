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

    if motor.adaptive_mesh_data.n_theta != minimum_theta_cell:
        motor.adaptive_mesh_data.n_theta = minimum_theta_cell 
        motor.just_changed("mesh")

    motor.require("drive")

    phase_number = motor.winding_data.phase
    flux_linkage = np.zeros((phase_number + 3, n_point))
    cogging = np.zeros((2, n_point))
    mst_data = np.zeros((5, n_point))
    current = np.zeros((3 + phases, n_point))

    # --- VONG LAP 1: GIAI COGGING TORQUE (KHONG TAI) ---
    if solve_cogging:
        for i in tqdm(range(n_point), desc="Solving Cogging", disable=not debug):
            if callback:
                callback(f"Solving Cogging step {i+1}/{n_point}", int(15 + (i/n_point)*40))
            
            motor.drive.apply_winding_excitation(excitation = False)
            motor.reluctance_network.solve(
                max_relative_residual = max_relative_residual,
                max_iteration = max_iteration,
                material_relax = material_relax, 
                damping_factor = 1.0,   
                debug = debug
            )
            cogging[:, i] = motor.maxwell_stress_tensor().mst_result[3:5]
            motor.rotate_rotor(n_step = 1)
        
        # Reset rotor ve vi tri ban dau de giai Standard
        motor.rotate_rotor(n_step = -n_point)

    # --- VONG LAP 2: GIAI STANDARD (CO TAI) ---
    for i in tqdm(range(n_point), desc="Solving Standard", disable=not debug):
        if callback:
            callback(f"Solving Standard step {i+1}/{n_point}", int(55 + (i/n_point)*40))
        
        motor.drive.apply_winding_excitation(excitation = True)
        motor.reluctance_network.solve(
            max_relative_residual = max_relative_residual,
            max_iteration = max_iteration,
            material_relax = material_relax, 
            damping_factor = 1.0,   
            debug = debug
        )
        
        motor.reluctance_network.add_elements_lite()
        flux_linkage[:, i] = motor.reluctance_network.get_flux_linkage().flux_linkage[:, 0]
        mst_data[:, i] = motor.maxwell_stress_tensor().mst_result[:]
        current[:, i] = motor.drive.debug_current()[:]
        
        # Xoay theo buoc nhay de cover het symmetry_angle
        motor.rotate_rotor(n_step = angle_factor)

    if callback: callback("Post-processing data", 95)
    
    use_symmetry = motor.mesh.periodic_boundary
    if use_symmetry:
        flux_linkage[:-1] *= symmetry_factor
        mst_data[:-1] *= symmetry_factor
        cogging[:-1] *= symmetry_factor

    shaft_speed = motor.mechanical.shaft_speed * (pi/30)
    # Tinh Back-EMF tu cac hang pha (index 2 tro di)
    back_emf = periodic_derivative(data=flux_linkage[2:], half_open_interval=True).derivative * shaft_speed 
    
    mst_data = duplicate_data(data=mst_data, half_open_interval=True).duplicated_data
    cogging = duplicate_data(data=cogging, half_open_interval=True).duplicated_data

    motor.record.flux_linkage = flux_linkage.copy()
    motor.record.back_emf = back_emf.copy()
    motor.record.mst_data = mst_data.copy()
    motor.record.cogging = cogging.copy()
    motor.record.currents = current.copy()

    if callback: callback("Analysis Completed", 100)
    return None