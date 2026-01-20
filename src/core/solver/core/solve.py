from src.core.solver.utils.fixed_point_iteration_for_magnetic_potential import fix_point_iteration_for_magnetic_potential
from src.core.solver.utils.adaptive_broyden_iteration_for_magnetic_potential import adaptive_broyden_iteration_for_magnetic_potential
from src.core.solver.utils.broyden_iteration_for_magnetic_potential import broyden_iteration_for_magnetic_potential
def solve(reluctance_network,
          method = "fixed_point_iteration",
          load_step = 1,
          max_relative_residual = 0.05,
          max_iteration=50,
          material_relax=0.5, 
          damping_factor = 0.05,   
          debug = True):
    
    if method == "fixed_point_iteration":
        if reluctance_network.system_variable == "loop_flux":
            pass
        elif reluctance_network.system_variable == "magnetic_potential":
            fix_point_iteration_for_magnetic_potential(reluctance_network= reluctance_network,
                                                       max_iteration= max_iteration,
                                                       material_relax= material_relax,
                                                       max_relative_residual = max_relative_residual,
                                                       damping_factor= damping_factor,
                                                       debug = debug)
        else:
            print("system variable is undefined")
    elif method == "newton_raphson":
        if reluctance_network.system_variable == "loop_flux":
            pass
        elif reluctance_network.system_variable == "magnetic_potential":
            pass
        else:
            print("system variable is undefined")

    elif method == "fixed_point_iteration_load_step":
        if reluctance_network.system_variable == "magnetic_potential":
            pass

    elif method == "broyden":
        if reluctance_network.system_variable == "magnetic_potential":
            broyden_iteration_for_magnetic_potential(reluctance_network= reluctance_network,
                                                     max_iteration= max_iteration,
                                                     material_relax = material_relax,
                                                     max_relative_residual = max_relative_residual,
                                                     damping_factor= damping_factor,
                                                     debug = debug)
    elif method == "adaptive_broyden":
        if reluctance_network.system_variable == "magnetic_potential":
            adaptive_broyden_iteration_for_magnetic_potential(reluctance_network= reluctance_network,
                                                     max_iteration= max_iteration,
                                                     material_relax = material_relax,
                                                     max_relative_residual = max_relative_residual,
                                                     damping_factor= damping_factor,
                                                     debug = debug)

    else:
        print("method is undefined")