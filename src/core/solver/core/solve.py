import numpy as np
import time
from pypardiso import spsolve as pardiso_solve
from scipy.sparse.linalg import norm

def solve(solver):
    reluctance_network = solver.reluctance_network
    convergence_settings = solver.convergence_settings
    # Lay debug tu general_options
    debug = reluctance_network.calculation_data.general_options.debug

    material_relax = convergence_settings.material_relax
    max_iteration = convergence_settings.max_iteration
    max_relative_residual = convergence_settings.max_relative_residual
    damping_factor = convergence_settings.damping_factor
    relaxation_history = convergence_settings.relaxation_history
    
    stats = {
        "update_network": 0.0,
        "create_equation": 0.0,
        "direct_solve": 0.0,
        "other": 0.0
    }
    t_start_total = time.perf_counter()

    # Doc gia tri relaxation_decay dang dung
    factor_1 = convergence_settings.relaxation_decay
    G_c, Y_c, R_c, B_c, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[94m", "\033[0m"
    best_residual_history = []
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    
    x_k = reluctance_network.magnetic_potential.data.flatten(order='F')[:-1]
    best_pot_data = reluctance_network.magnetic_potential.data.copy()
    best_phi = float('inf') 
    current_relax = material_relax
    total_iteration = 0

    def compute_system(x_vec, relax):
        t0 = time.perf_counter()
        reluctance_network.magnetic_potential.data = np.append(x_vec, 0.0).reshape(mag_pot_shape, order='F')
        reluctance_network.update_reluctance_network(
            magnetic_potential=reluctance_network.magnetic_potential,
            update_for_magnetic_potential=True,
            material_relaxation_factor=relax, 
            delta_mu_max=-1 
        )
        t1 = time.perf_counter()
        stats["update_network"] += (t1 - t0)

        comp = reluctance_network.create_magnetic_potential_equation(load_factor=1.0)
        t2 = time.perf_counter()
        stats["create_equation"] += (t2 - t1)

        F_x = comp.G.dot(x_vec) - comp.J
        return F_x, comp.G, comp.J

    F_k, G_k, J_k = compute_system(x_k, current_relax)
    
    for j in range(1, max_iteration + 1):
        total_iteration = j
        try:
            t_s0 = time.perf_counter()
            delta_x = pardiso_solve(G_k, -F_k)
            stats["direct_solve"] += (time.perf_counter() - t_s0)
            
        except Exception as e:
            if debug: print(f"{R_c}Solver Error: {e}{RESET}")
            break

        x_next = x_k + damping_factor * delta_x
        F_next, G_next, J_next = compute_system(x_next, current_relax)
        
        t_o0 = time.perf_counter()
        phi_true = np.linalg.norm(F_next) / (np.linalg.norm(J_next) + 1e-12)
        best_residual_history.append(phi_true)

        if debug:
            color = G_c if phi_true <= max_relative_residual else (R_c if phi_true >= best_phi else RESET)
            print(f"{color}Iteration {j}: relative residual = {phi_true*100:.2f}%, Relax = {current_relax:.4f}{RESET}")

        if phi_true <= max_relative_residual:
            best_phi = phi_true
            best_pot_data = reluctance_network.magnetic_potential.data.copy()
            stats["other"] += (time.perf_counter() - t_o0)
            break
        
        if phi_true < best_phi:
            best_phi = phi_true
            best_pot_data = reluctance_network.magnetic_potential.data.copy()
        elif phi_true > best_phi * 2.0:
            stats["other"] += (time.perf_counter() - t_o0)
            break

        current_relax *= factor_1
        F_next, G_next, J_next = compute_system(x_next, current_relax)

        G_k, x_k, F_k = G_next, x_next, F_next
        stats["other"] += (time.perf_counter() - t_o0)

    # Cap nhat so buoc lap vao hang 2 cua relaxation_history
    decay_values = relaxation_history[0, :]
    idx = np.argmin(np.abs(decay_values - factor_1))
    relaxation_history[1, idx] = total_iteration

    # Luu lich su sai so vao setting de find_relaxation_decay co the su dung neu can
    convergence_settings.relaxation_history_current = best_residual_history

    t_end_total = time.perf_counter()
    total_time = t_end_total - t_start_total

    if debug:
        print("\n" + "="*50)
        print(f"{B_c}PERFORMANCE SUMMARY (PYPARDISO SOLVER){RESET}")
        print("-"*50)
        for task, duration in stats.items():
            percentage = (duration / total_time) * 100
            print(f"{task.replace('_', ' ').title():<20}: {duration:>8.4f} s ({percentage:>6.2f}%)")
        print("-"*50)
        print(f"{'Total Solve Time':<20}: {total_time:>8.4f} s (100.00%)")
        print("="*50 + "\n")

    reluctance_network.magnetic_potential.data = best_pot_data
    reluctance_network.refresh_elements()

    solver.find_relaxation_decay()
    return best_phi, best_residual_history


