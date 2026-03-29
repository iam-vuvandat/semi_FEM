import numpy as np
import time
from pypardiso import spsolve as pardiso_solve
from scipy.sparse.linalg import norm

def solve(reluctance_network, 
          max_iteration=50,
          max_relative_residual=0.05, 
          material_relax=0.2, 
          damping_factor=0.5,   
          debug=True):
    
    stats = {
        "update_network": 0.0,
        "create_equation": 0.0,
        "direct_solve": 0.0,
        "other": 0.0
    }
    t_start_total = time.perf_counter()

    factor_1 = 0.5
    G_c, Y_c, R_c, B_c, RESET = "\033[92m", "\033[93m", "\033[91m", "\033[94m", "\033[0m"
    best_residual_history = []
    mag_pot_shape = reluctance_network.magnetic_potential.data.shape
    
    x_k = reluctance_network.magnetic_potential.data.flatten(order='F')[:-1]
    best_pot_data = reluctance_network.magnetic_potential.data.copy()
    best_phi = float('inf') 
    current_relax = material_relax

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
        try:
            # Giai truc tiep bang PyPardiso (Intel MKL Pardiso)
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
        best_residual_history.append(phi_true)
        stats["other"] += (time.perf_counter() - t_o0)

    t_end_total = time.perf_counter()
    total_time = t_end_total - t_start_total
    



    # -- Debug -- 
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
    return best_phi, best_residual_history