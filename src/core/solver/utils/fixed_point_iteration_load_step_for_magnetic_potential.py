import numpy as np
from scipy.sparse.linalg import spsolve, norm, onenormest, splu, LinearOperator

def fix_point_iteration_load_step_for_magnetic_potential(reluctance_network, 
                                               max_iteration=50,
                                               load_step =5,
                                               material_relax=0.2, 
                                               damping_factor = 0.1,   
                                               debug = True):
    
    pass