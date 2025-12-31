from solver.utils.fixed_point_iteration import fix_point_iteration
from solver.utils.newton_raphson import newton_raphson

def solve_magnetic_equation(reluctance_network, 
                            method="fixed_point_iteration",
                            max_iteration=50, 
                            max_relative_residual=1e-4, 
                            adaptive_damping_factor=(1.0, 0.1),
                            load_step=5, 
                            debug=True):

    if method == "fixed_point_iteration":
        fix_point_iteration(reluctance_network= reluctance_network,
                            max_iteration= max_iteration,
                            max_relative_residual= max_relative_residual,
                            adaptive_damping_factor= adaptive_damping_factor,
                            load_step= load_step,
                            debug= debug)
        
    if method == "newton_raphson":
        newton_raphson(reluctance_network= reluctance_network,
                            max_iteration= max_iteration,
                            max_relative_residual= max_relative_residual,
                            adaptive_damping_factor= adaptive_damping_factor,
                            load_step= load_step,
                            debug= debug)