import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def function_normalized_exp(position, order=4):
    return (1 - np.exp(-order * position)) / (1 - np.exp(-order))

def find_load_factor(load_step, order=4):
    x = np.linspace(0, 1, load_step + 1)[1:]
    return function_normalized_exp(x, order=order)

def fix_point_iteration(reluctance_network, 
                        max_iteration=50, 
                        max_relative_residual=1e-4, 
                        adaptive_damping_factor=(1.0, 0.1),
                        load_step=10, 
                        debug=True):

    reluctance_network.set_reluctance_at_zero()
    if isinstance(max_iteration, tuple): 
        max_iteration = max_iteration[0]

    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()
    global_stable_checkpoint = current_magnetic_potential.copy()
    
    load_factors = find_load_factor(load_step=load_step, order=1)
    smart_damping = np.linspace(adaptive_damping_factor[0], adaptive_damping_factor[1], load_step)
    
    residual_history = []
    load_step_indices = []

    GREEN, RED, WHITE, RESET = "\033[92m", "\033[91m", "\033[97m", "\033[0m"

    for i in range(load_step):
        current_max_iter = max_iteration * 2 if i == load_step - 1 else max_iteration
        current_load = load_factors[i]
        
        initial_step_damping = smart_damping[i]
        current_damping = initial_step_damping
        
        backtrack_count = 0
        backtrack_limit = max_iteration // 2 
        
        j = 0
        while j < current_max_iter:
            if j == 0 and i > 0:
                load_step_indices.append(len(residual_history))

            comp = reluctance_network.create_magnetic_potential_equation(
                first_time=(i == 0 and j == 0),
                load_factor=current_load, debug=False
            )
            G_old, J = comp.G, comp.J
            norm_J = np.linalg.norm(J) + 1e-12
            
            p_sol = spsolve(G_old, J)
            p_full = np.append(p_sol, 0.0).reshape(magnetic_potential_shape, order='F')

            direction = p_full - current_magnetic_potential
            test_potential = current_magnetic_potential + current_damping * direction
            
            reluctance_network.magnetic_potential.data = test_potential
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)

            comp_new = reluctance_network.create_magnetic_potential_equation(
                first_time=False, load_factor=current_load, debug=False
            )
            P_active = test_potential.flatten(order='F')[:-1]
            res_val = np.linalg.norm(comp_new.G.dot(P_active) - J) / norm_J

            if debug:
                if j == 0:
                    color = WHITE
                elif len(residual_history) > 0:
                    color = GREEN if res_val < residual_history[-1] else RED
                else:
                    color = RESET
                
                print(f"{color}Step {i+1}/{load_step}, Iter {j+1}: Damping = {current_damping:.4f}, Res = {res_val*100:.4f}%{RESET}")

            if j > 0 and len(residual_history) > 0:
                if res_val > residual_history[-1] * 1.01:
                    if backtrack_count < backtrack_limit and current_damping > (0.1 * initial_step_damping):
                        backtrack_count += 1
                        current_magnetic_potential = local_stable_checkpoint.copy()
                        reluctance_network.magnetic_potential.data = current_magnetic_potential
                        reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
                        
                        current_damping *= 0.8
                        if debug:
                            print(f"   {RED}[!] Backtrack {backtrack_count}. Damping -> {current_damping:.4f}{RESET}")
                        continue
                    else:
                        if debug:
                            print(f"   {RED}[!] Thoát bước {i+1}. Reset về nghiệm ổn định Global.{RESET}")
                        current_magnetic_potential = global_stable_checkpoint.copy()
                        break

            local_stable_checkpoint = test_potential.copy() 
            global_stable_checkpoint = test_potential.copy() 
            current_magnetic_potential = test_potential.copy()
            residual_history.append(res_val)

            if res_val < max_relative_residual:
                break
            j += 1

    reluctance_network.add_elements_lite()

    if debug and residual_history:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        if len(residual_history) > 2:
            residual_history[0] = residual_history[1] * 1.5
            
        ax.plot(residual_history, color='teal', marker='o', markersize=3, label='Equation Residual')
        for idx in load_step_indices:
            ax.axvline(x=idx, color='red', linestyle='--', alpha=0.3)
            
        ax.set_yscale('log')
        ax.set_xlabel("Cumulative Iterations")
        ax.set_ylabel("Relative Residual (||GP-J||/||J||)")
        ax.set_title("Robust Convergence History (Start with Smart Damping)")
        ax.axhline(y=max_relative_residual, color='orange', linestyle=':', label='Target')
        ax.grid(True, which="both", alpha=0.2)
        ax.legend()
        plt.tight_layout()
        plt.show()
        reluctance_network.show()

    
    