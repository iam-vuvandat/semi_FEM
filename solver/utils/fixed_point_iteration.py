import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve

def function_nonlinear_load(load_step, order=2):
    x = np.linspace(0, 1, load_step + 1)[1:]
    return (1 - np.exp(-order * x)) / (1 - np.exp(-order))

def fix_point_iteration(reluctance_network, 
                        max_iteration=50, 
                        max_relative_residual=3e-2, 
                        adaptive_damping_factor=(1.0, 0.1),
                        load_step=10, 
                        anderson_m=5,
                        debug=True):

    reluctance_network.set_reluctance_at_zero()
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()
    last_step_checkpoint = current_magnetic_potential.copy()
    
    load_queue = list(function_nonlinear_load(load_step, order=2))
    
    def get_damping(load):
        return np.interp(load, [0, 1], [adaptive_damping_factor[0], adaptive_damping_factor[1]])
    
    residual_history = []
    load_step_indices = []
    last_converged_load = 0.0
    damping_multiplier = 1.0

    GREEN, RED, WHITE, YELLOW, CYAN, RESET = "\033[92m", "\033[91m", "\033[97m", "\033[93m", "\033[96m", "\033[0m"

    while load_queue:
        current_load = load_queue.pop(0)
        base_damping = get_damping(current_load)
        current_damping = base_damping * damping_multiplier
        
        current_magnetic_potential = last_step_checkpoint.copy()
        reluctance_network.magnetic_potential.data = current_magnetic_potential
        reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
        
        xs, fs = [], []
        converged_this_step = False
        
        j = 0
        limit_j = max_iteration * 2 if current_load > 0.8 else max_iteration
        
        while j < limit_j:
            if j == 0: load_step_indices.append(len(residual_history))

            comp = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
            G_old, J = comp.G, comp.J
            norm_J = np.linalg.norm(J) + 1e-12
            
            p_sol = spsolve(G_old, J)
            g_x_full = np.append(p_sol, 0.0)
            
            x_k = current_magnetic_potential.flatten(order='F')
            f_k = g_x_full - x_k
            
            reluctance_network.magnetic_potential.data = g_x_full.reshape(magnetic_potential_shape, order='F')
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            comp_new = reluctance_network.create_magnetic_potential_equation(load_factor=current_load, debug=False)
            res_val = np.linalg.norm(comp_new.G.dot(p_sol) - J) / norm_J

            if debug:
                color = WHITE if j == 0 else (GREEN if (len(residual_history) > 0 and res_val < residual_history[-1]) else RED)
                print(f"{color}Load {current_load:.4f}, Iter {j+1}: Damping = {current_damping:.4f}, Res = {res_val*100:.4f}%{RESET}")

            if j > 0 and len(residual_history) > 0:
                if res_val > residual_history[-1] * 1.05:
                    if debug: print(f"   {RED}[!] Divergence! L2 Backtrack: Sub-step + Damping reduction...{RESET}")
                    break 

            residual_history.append(res_val)

            if res_val < max_relative_residual:
                converged_this_step = True
                last_step_checkpoint = g_x_full.reshape(magnetic_potential_shape, order='F')
                last_converged_load = current_load
                damping_multiplier = 1.0
                break

            if anderson_m == 0 or j == 0:
                x_next = x_k + current_damping * f_k
            else:
                xs.append(x_k); fs.append(f_k)
                if len(xs) > anderson_m: xs.pop(0); fs.pop(0)
                m_k = len(xs) - 1
                if m_k > 0:
                    F = np.array([fs[k+1] - fs[k] for k in range(m_k)]).T
                    X = np.array([xs[k+1] - xs[k] for k in range(m_k)]).T
                    try:
                        gamma = np.linalg.lstsq(F, f_k, rcond=None)[0]
                        x_next = (x_k + current_damping * f_k) - (X + current_damping * F).dot(gamma)
                    except: x_next = x_k + current_damping * f_k
                else: x_next = x_k + current_damping * f_k

            current_magnetic_potential = x_next.reshape(magnetic_potential_shape, order='F')
            j += 1
            
        if not converged_this_step:
            mid_load = (last_converged_load + current_load) / 2
            if abs(current_load - last_converged_load) > 1e-5:
                load_queue.insert(0, current_load)
                load_queue.insert(0, mid_load)
                damping_multiplier *= 0.5
                if debug:
                    print(f"   {YELLOW}[!!] L2 TRIGGERED: Load {current_load:.4f} failed.")
                    print(f"   {CYAN}>>> Sub-step: {mid_load:.4f} | New Damping Scale: {damping_multiplier}{RESET}")
            else:
                if debug: print(f"   {RED}[!!!] FATAL: Convergence limit reached at {current_load:.4f}{RESET}")
                break

    reluctance_network.add_elements_lite()

    if debug and residual_history:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        ax.plot(residual_history, color='teal', marker='o', markersize=2, label='Equation Residual')
        for idx in load_step_indices:
            ax.axvline(x=idx, color='red', linestyle='--', alpha=0.15)
        ax.set_yscale('log')
        ax.set_xlabel("Total Iterations")
        ax.set_ylabel("Relative Residual")
        ax.set_title("3D MBGRN: Hybrid Sub-stepping & Damping Reduction")
        ax.axhline(y=max_relative_residual, color='orange', linestyle=':', label='Target')
        ax.grid(True, which="both", alpha=0.2)
        plt.show()