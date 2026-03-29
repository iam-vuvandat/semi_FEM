import paths
import numpy as np
import math 
from tqdm import tqdm

pi = math.pi
from src.core.solver.utils.periodic_derivative import periodic_derivative
from src.core.solver.utils.duplicate_data import duplicate_data
from src.core.solver.utils.calculate_line_to_line_back_emf import calculate_line_to_line_back_emf


def analysis_motor(motor, callback = None):

    # require calculation data
    motor.require("calculation_data")
    calculation_data = motor.calculation_data
    conv = calculation_data.convergence_settings
    gen = calculation_data.general_options
    
    max_relative_residual = conv.max_relative_residual
    max_iteration = conv.max_iteration
    material_relax = conv.material_relax
    
    solve_cogging = gen.solve_cogging
    n_point = gen.n_point
    debug = gen.debug
    solve_only_1_step = gen.solve_only_1_step

    if solve_only_1_step:
        n_point = 1

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

    periodic_factor = 1 
    if motor.mesh.periodic_boundary is True:
        periodic_factor = symmetry_factor

    phase_number = motor.winding_data.phase
    flux_linkage = np.zeros((phase_number + 3, n_point))
    cogging = np.zeros((2, n_point))
    mst_data = np.zeros((5, n_point))
    current = np.zeros((3 + phases, n_point))

    mechanical_power = np.zeros((2,n_point))

    if solve_cogging:
        motor.mechanical.reset_motor_position()
        for i in tqdm(range(n_point), desc="Solving Cogging", disable=not debug):
           
            
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
        
        motor.mechanical.reset_motor_position()

    for i in tqdm(range(n_point), desc="Solving Standard", disable=not debug):
        
        
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
        
        motor.rotate_rotor(n_step = angle_factor)


    # Export inductance map:
    motor.mechanical.reset_motor_position()
    export_inductance_options = motor.calculation_data.export_inductance_options
    export_inductance = export_inductance_options.export_inductance

    if export_inductance is True:
        current_min = export_inductance_options.current_min
        current_max = export_inductance_options.current_max
        current_resolution = export_inductance_options.current_resolution

        id_vector = np.linspace(-current_max, -current_min if current_min != 0 else 0, current_resolution)
        iq_vector = np.linspace(current_min, current_max, current_resolution)

        ld_map = np.zeros((current_resolution, current_resolution))
        lq_map = np.zeros((current_resolution, current_resolution))

        # 1. Giai diem khong tai (id=0, iq=0) de lay Psi_pm
        motor.drive.apply_manual_winding_excitation(id=0.0, iq=0.0) # Su dung method moi
        motor.reluctance_network.solve(
            max_relative_residual = conv.max_relative_residual,
            max_iteration = conv.max_iteration,
            material_relax = conv.material_relax,
            debug = False
        )
        psi_pm = motor.reluctance_network.get_flux_linkage().flux_linkage[0, 0] * periodic_factor
        
        for i, id_val in enumerate(tqdm(id_vector, desc="Exporting Ld Map", disable=not debug)):
            for j, iq_val in enumerate(iq_vector):
                # Su dung dung method: apply_manual_winding_excitation
                motor.drive.apply_manual_winding_excitation(id=id_val, iq=iq_val)
                
                motor.reluctance_network.solve(
                    max_relative_residual = conv.max_relative_residual,
                    max_iteration = conv.max_iteration,
                    material_relax = conv.material_relax,
                    debug = False
                )
                
                flux_dq = motor.reluctance_network.get_flux_linkage().flux_linkage[:2, 0] * periodic_factor
                
                ld_map[i, j] = (flux_dq[0] - psi_pm) / id_val if abs(id_val) > 1e-6 else 0
                lq_map[i, j] = flux_dq[1] / iq_val if abs(iq_val) > 1e-6 else 0

        motor.record.id_grid = id_vector
        motor.record.iq_grid = iq_vector
        motor.record.ld_map = ld_map
        motor.record.lq_map = lq_map


    shaft_speed = motor.mechanical.shaft_speed * (pi/30)

    flux_linkage[:-1] *= periodic_factor
    mst_data[:-1] *= periodic_factor
    mechanical_power = mst_data[[3,-1],:]
    mechanical_power[0,:] *= shaft_speed
    cogging[:-1] *= periodic_factor

    
    back_emf = periodic_derivative(data=flux_linkage[2:], half_open_interval=True).derivative * shaft_speed 
    back_emf_line = calculate_line_to_line_back_emf(data_numpy=back_emf)

    mst_data = duplicate_data(data=mst_data, half_open_interval=True).duplicated_data
    cogging = duplicate_data(data=cogging, half_open_interval=True).duplicated_data

    motor.record.flux_linkage = flux_linkage.copy()
    motor.record.back_emf = back_emf.copy()
    motor.record.back_emf_line = back_emf_line.copy()
    motor.record.mst_data = mst_data.copy()
    motor.record.mechanical_power = mechanical_power.copy()
    motor.record.cogging = cogging.copy()
    motor.record.currents = current.copy()
    motor.record.average_mechanical_power =   mechanical_power[0,:].mean()

    
    return None
