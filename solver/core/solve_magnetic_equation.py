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
                            load_step = 5, 
                            debug=True):
    
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape
    current_magnetic_potential = reluctance_network.magnetic_potential.data
    
    load_factors = np.linspace(0, 1, load_step+1)[1:]

    for i in range(load_step):
        for j in range(max_iteration):
            if j == 0:
                current_damping = first_step_damping_factor
            else:
                current_damping = damping_factor

            if i == 0 and j == 0 :
                first_time = True
            else:
                first_time = False
            
            equation_component = reluctance_network.create_magnetic_potential_equation(first_time = first_time,
                                                                                        load_factor = load_factors[i])
            G = equation_component.G
            J = equation_component.J

            solved_vector = spsolve(G, J)
            solved_vector_with_ref = np.append(solved_vector, 0.0)
            magnetic_potential_solved = solved_vector_with_ref.reshape(magnetic_potential_shape, order='F')
            next_magnetic_potential = (current_magnetic_potential * (1 - current_damping) + 
                                   magnetic_potential_solved * current_damping)
        
            current_magnetic_potential = next_magnetic_potential
            reluctance_network.magnetic_potential.data = next_magnetic_potential
            reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)


    