import numpy as np
from pypardiso import spsolve as pardiso_solve
from scipy.sparse.linalg import norm

def _compute_system(reluctance_network, magnetic_potential, relaxation_factor, magnetic_potential_shape):
    reluctance_network.magnetic_potential.data = np.append(magnetic_potential, 0.0).reshape(magnetic_potential_shape, order='F')
    reluctance_network.update_reluctance_network(
        magnetic_potential=reluctance_network.magnetic_potential,
        update_for_magnetic_potential=True,
        material_relaxation_factor=relaxation_factor, 
        delta_mu_max=-1 
    )

    equation_components = reluctance_network.create_magnetic_potential_equation(load_factor=1.0)

    residual_vector = equation_components.G.dot(magnetic_potential) - equation_components.J
    return residual_vector, equation_components.G, equation_components.J

def _calculate_relative_residual(residual_vector, current_source_vector):
    return np.linalg.norm(residual_vector) / (np.linalg.norm(current_source_vector) + 1e-12)

def _evaluate_convergence(true_residual, last_iteration_residual, best_residual, max_relative_residual):
    if true_residual <= max_relative_residual:
        return True, True
    if true_residual < last_iteration_residual * 0.90:
        return False, True
    if true_residual > best_residual * 2.0:
        return True, False
    return False, False

def _update_history_settings(convergence_settings, relaxation_decay, total_iteration, best_residual_history):
    decay_values = convergence_settings.relaxation_history[0, :]
    idx = np.argmin(np.abs(decay_values - relaxation_decay))
    convergence_settings.relaxation_history[1, idx] = total_iteration

    convergence_settings.relaxation_history_current = best_residual_history

def solve(solver):
    reluctance_network = solver.reluctance_network
    record = reluctance_network.motor.record
    convergence_settings = solver.convergence_settings

    enable_potential_tracking = convergence_settings.enable_potential_tracking
    initial_material_relax = convergence_settings.material_relax
    exact_residual_error = convergence_settings.exact_residual_error
    max_iteration = convergence_settings.max_iteration
    max_relative_residual = convergence_settings.max_relative_residual
    damping_factor = convergence_settings.damping_factor
    relaxation_history = convergence_settings.relaxation_history
    relaxation_decay = convergence_settings.relaxation_decay
    force_use_full_iteration = convergence_settings.force_use_full_iteration
    
    green_color, yellow_color, red_color, blue_color, color_reset = "\033[92m", "\033[93m", "\033[91m", "\033[94m", "\033[0m"
    best_residual_history = []
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    
    magnetic_potential_current = reluctance_network.magnetic_potential.data.flatten(order='F')[:-1]
    best_potential_data = reluctance_network.magnetic_potential.data.copy()
    best_residual = float('inf') 
    material_relax = initial_material_relax
    total_iteration = 0

    if not hasattr(record, 'solver_history'):
        record.solver_history = []

    current_run_data = []
    current_run_potentials = []

    residual_current, permeance_matrix_current, current_source_current = _compute_system(reluctance_network, magnetic_potential_current, material_relax, magnetic_potential_shape)
    
    last_iteration_residual = _calculate_relative_residual(residual_current, current_source_current)

    for j in range(1, max_iteration + 1):
        total_iteration = j
        
        delta_magnetic_potential = pardiso_solve(permeance_matrix_current, -residual_current)

        magnetic_potential_next = magnetic_potential_current + damping_factor * delta_magnetic_potential
        residual_next, permeance_matrix_next, current_source_next = _compute_system(reluctance_network, magnetic_potential_next, material_relax, magnetic_potential_shape)
        
        true_residual = _calculate_relative_residual(residual_next, current_source_next)
        best_residual_history.append(true_residual)

        residual_change_pct = ((true_residual - last_iteration_residual) / (last_iteration_residual + 1e-12)) * 100

        current_run_data.append([j, true_residual, material_relax, relaxation_decay])
        if enable_potential_tracking:
            current_run_potentials.append(np.append(magnetic_potential_next, 0.0))

        color = green_color if true_residual <= max_relative_residual else (red_color if true_residual >= best_residual else color_reset)
        print(f"{color}Iteration {j}: relative residual = {true_residual*100:.6f}% ({residual_change_pct:+.2f}%), Relax = {material_relax:.6f}, Decay = {relaxation_decay:.6f}{color_reset}")

        if true_residual <= max_relative_residual:
            print(f"{green_color}   --> [CONVERGED] Target residual criteria satisfied.{color_reset}")

        is_break, is_best = _evaluate_convergence(true_residual, last_iteration_residual, best_residual, max_relative_residual)

        if is_best:
            if true_residual < best_residual:
                best_residual = true_residual
                best_potential_data = reluctance_network.magnetic_potential.data.copy()

            permeance_matrix_current = permeance_matrix_next
            magnetic_potential_current = magnetic_potential_next
            residual_current = residual_next
            last_iteration_residual = true_residual
        else:
            if relaxation_decay == 1.0:
                permeance_matrix_current = permeance_matrix_next
                magnetic_potential_current = magnetic_potential_next
                residual_current = residual_next
                last_iteration_residual = true_residual
            else:
                if true_residual > best_residual * 2.0:
                    reason = "Severe divergence detected"
                elif true_residual >= last_iteration_residual:
                    reason = "Residual increased or stagnated"
                else:
                    reason = "Insufficient residual reduction (< 10%)"
                
                print(f"{yellow_color}   --> [BACKTRACKING] Reason: {reason}. Rolling back potential and applying decay factor.{color_reset}")
                
                material_relax *= relaxation_decay
                
                magnetic_potential_current = best_potential_data.flatten(order='F')[:-1]
                residual_current, permeance_matrix_current, current_source_current = _compute_system(reluctance_network, magnetic_potential_current, material_relax, magnetic_potential_shape)
                last_iteration_residual = best_residual

        if is_break:
            if not force_use_full_iteration or (true_residual <= max_relative_residual):
                if true_residual > best_residual * 2.0:
                    print(f"{red_color}   --> [TERMINATED] Solver stopped due to divergence limit.{color_reset}")
                break

    record.solver_history.append(np.array(current_run_data))
    if enable_potential_tracking:
        if not hasattr(record, 'magnetic_potential_history'):
            record.magnetic_potential_history = []
        record.magnetic_potential_history.append(np.array(current_run_potentials))

    reluctance_network.magnetic_potential.data = best_potential_data
    reluctance_network.refresh_elements()
    
    return best_residual, best_residual_history