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

def _evaluate_convergence(true_residual, best_residual, max_relative_residual):
    if true_residual <= max_relative_residual:
        return True, True
    if true_residual < best_residual:
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
    convergence_settings = solver.convergence_settings

    initial_material_relax = convergence_settings.material_relax
    exact_residual_error = convergence_settings.exact_residual_error
    max_iteration = convergence_settings.max_iteration
    max_relative_residual = convergence_settings.max_relative_residual
    damping_factor = convergence_settings.damping_factor
    relaxation_history = convergence_settings.relaxation_history
    
    relaxation_decay = convergence_settings.relaxation_decay
    green_color, yellow_color, red_color, blue_color, color_reset = "\033[92m", "\033[93m", "\033[91m", "\033[94m", "\033[0m"
    best_residual_history = []
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    
    magnetic_potential_current = reluctance_network.magnetic_potential.data.flatten(order='F')[:-1]
    best_potential_data = reluctance_network.magnetic_potential.data.copy()
    best_residual = float('inf') 
    material_relax = initial_material_relax
    total_iteration = 0

    residual_current, permeance_matrix_current, current_source_current = _compute_system(reluctance_network, magnetic_potential_current, material_relax, magnetic_potential_shape)
    
    for j in range(1, max_iteration + 1):
        total_iteration = j
        
        delta_magnetic_potential = pardiso_solve(permeance_matrix_current, -residual_current)

        magnetic_potential_next = magnetic_potential_current + damping_factor * delta_magnetic_potential
        residual_next, permeance_matrix_next, current_source_next = _compute_system(reluctance_network, magnetic_potential_next, material_relax, magnetic_potential_shape)
        
        true_residual = _calculate_relative_residual(residual_next, current_source_next)
        best_residual_history.append(true_residual)

        color = green_color if true_residual <= max_relative_residual else (red_color if true_residual >= best_residual else color_reset)
        print(f"{color}Iteration {j}: relative residual = {true_residual*100:.2f}%, Relax = {material_relax:.4f}{color_reset}")

        is_break, is_best = _evaluate_convergence(true_residual, best_residual, max_relative_residual)

        if is_best:
            best_residual = true_residual
            best_potential_data = reluctance_network.magnetic_potential.data.copy()

            # Khi sai số giảm tốt: GIỮ NGUYÊN material_relax và tịnh tiến hệ thống
            permeance_matrix_current = permeance_matrix_next
            magnetic_potential_current = magnetic_potential_next
            residual_current = residual_next
        else:
            # Khi sai số TĂNG: GIẢM material_relax và khôi phục về trạng thái tốt nhất
            material_relax *= relaxation_decay
            
            magnetic_potential_current = best_potential_data.flatten(order='F')[:-1]
            residual_current, permeance_matrix_current, current_source_current = _compute_system(reluctance_network, magnetic_potential_current, material_relax, magnetic_potential_shape)

        if is_break:
            break

    _update_history_settings(convergence_settings, relaxation_decay, total_iteration, best_residual_history)

    reluctance_network.magnetic_potential.data = best_potential_data
    reluctance_network.refresh_elements()
    
    return best_residual, best_residual_history