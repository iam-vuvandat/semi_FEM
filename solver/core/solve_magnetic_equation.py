import numpy as np
import matplotlib.pyplot as plt
from scipy.sparse.linalg import spsolve, MatrixRankWarning
from tqdm import tqdm
import warnings

def solve_magnetic_equation(reluctance_network, 
                            max_iteration=50, 
                            max_relative_residual=1e-4, 
                            first_step_damping_factor = 0.1,
                            damping_factor=0.5, 
                            debug=True):
    
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data
    
    residual_history = []
    
    iterator = range(max_iteration)
    if debug:
        iterator = tqdm(iterator, desc="Solving Magnetic Equation")

    final_residual = float('inf')
    is_converged = False
    
    for i in iterator:
        if i == 0:
            current_damping = 1.0
            first_time = True
        else:
            current_damping = damping_factor
            first_time = False
        
        equation_component = reluctance_network.create_magnetic_potential_equation(first_time=first_time)
        G = equation_component.G
        J = equation_component.J
        
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("error", category=MatrixRankWarning)
                solved_vector = spsolve(G, J)
        except Exception:
            return {"success": False}

        solved_vector_with_ref = np.append(solved_vector, 0.0)
        magnetic_potential_solved = solved_vector_with_ref.reshape(magnetic_potential_shape, order='F')

        if i == 0:
            current_relative_residual = first_step_damping_factor
        else:
            diff_norm = np.linalg.norm(magnetic_potential_solved - current_magnetic_potential)
            ref_norm = np.linalg.norm(current_magnetic_potential)
            current_relative_residual = diff_norm / (ref_norm + 1e-9)
        
        residual_history.append(current_relative_residual)
        final_residual = current_relative_residual

        if debug:
            iterator.set_postfix(residual=f"{current_relative_residual:.6e}")

        if i > 0 and current_relative_residual < max_relative_residual:
            reluctance_network.magnetic_potential.data = magnetic_potential_solved
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
            is_converged = True
            break
        
        next_magnetic_potential = (current_magnetic_potential * (1 - current_damping) + 
                                   magnetic_potential_solved * current_damping)
        
        current_magnetic_potential = next_magnetic_potential
        reluctance_network.magnetic_potential.data = next_magnetic_potential
        reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)

    if debug:
        plt.figure(figsize=(10, 6))
        plt.plot(range(len(residual_history)), residual_history, marker='o', linestyle='-', color='b')
        plt.axhline(y=max_relative_residual, color='r', linestyle='--')
        plt.title('Convergence Plot')
        plt.xlabel('Iteration')
        plt.ylabel('Relative Residual')
        plt.grid(True)
        plt.show()

    return {
        "success": is_converged,
        "iterations": i + 1,
        "final_residual": final_residual,
        "history": residual_history
    }