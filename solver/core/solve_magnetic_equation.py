import numpy as np
import matplotlib.pyplot as plt
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
from dataclasses import dataclass
from typing import Any, List

@dataclass
class SolverResult:
    potential: np.ndarray
    residual_history: List[float]
    figure: Any

def solve_magnetic_equation(reluctance_network, 
                            method="preconditioned_steepest_descent",
                            max_iteration=50, 
                            max_relative_residual=1e-4, 
                            adaptive_damping_factor=(1.0, 0.1),
                            load_step=5, 
                            debug=True):
    
    if isinstance(max_iteration, tuple):
        max_iteration = max_iteration[0]

    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()
    load_factors = np.linspace(0, 1, load_step + 1)[1:]
    residual_history = []
    load_step_indices = []

    for i in range(load_step):
        current_load = load_factors[i]
        
        for j in range(max_iteration):
            if j == 0 and i > 0:
                load_step_indices.append(len(residual_history))

            current_damping = adaptive_damping_factor[0] if j == 0 else adaptive_damping_factor[1]
            
            is_reset = (i == 0 and j == 0)
            comp = reluctance_network.create_magnetic_potential_equation(
                first_time=is_reset,
                load_factor=current_load,
                debug=False
            )
            
            if is_reset:
                current_magnetic_potential = reluctance_network.magnetic_potential.data.copy()

            G, J = comp.G, comp.J
            P_active = current_magnetic_potential.flatten(order='F')[:-1]

            if method == "fixed_point_iteration":
                p_sol = spsolve(G, J)
                p_full = np.append(p_sol, 0.0).reshape(magnetic_potential_shape, order='F')
                current_res = np.linalg.norm(p_full - current_magnetic_potential) / (np.linalg.norm(p_full) + 1e-12)
                next_p = (current_magnetic_potential * (1 - current_damping) + p_full * current_damping)

            elif method == "preconditioned_steepest_descent":
                res = J - G.dot(P_active)
                current_res = np.linalg.norm(res) / (np.linalg.norm(J) + 1e-12)
                step = spsolve(G, res)
                next_p = np.append(P_active + current_damping * step, 0.0).reshape(magnetic_potential_shape, order='F')

            residual_history.append(current_res)
            current_magnetic_potential = next_p
            reluctance_network.magnetic_potential.data = current_magnetic_potential
            reluctance_network.update_reluctance_network()

            if current_res < max_relative_residual:
                break

    fig, ax = plt.subplots(figsize=(10, 6))
    if len(residual_history) > 2:
        residual_history[0] = 2 * residual_history[1] - residual_history[2]

    ax.plot(residual_history, label=f"Method: {method}", marker='o', markersize=3)
    
    for idx in load_step_indices:
        ax.axvline(x=idx, color='r', linestyle='--', alpha=0.5)

    ax.set_yscale('log')
    ax.set_xlabel("Total Cumulative Iterations")
    ax.set_ylabel("Relative Residual (Log scale)")
    ax.set_title(f"Convergence History: {method}")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    
    if debug:
        plt.show()
    else:
        plt.close(fig)

    return SolverResult(potential=current_magnetic_potential, 
                        residual_history=residual_history, 
                        figure=fig)