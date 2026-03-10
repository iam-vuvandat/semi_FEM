import math

def init_solver(m3d,motor):

    setup_name = "Setup1"
    if setup_name in m3d.setup_names:
        m3d.delete_setup(setup_name)

    motor.require("mechanical")

    shaft_speed = motor.mechanical_data.shaft_speed # rpm
    shaft_speed *= 2 * math.pi / 60 # rad/s

    symmetry_factor = motor.mechanical.symmetry_factor 
    theta_sweep = 2 * math.pi / symmetry_factor # rad 

    stop_time = (theta_sweep / shaft_speed) * 1000 # ms
    stop_time_str = f"{stop_time}ms"

    n_point = motor.calculation_data.general_options.n_point 
    time_step = stop_time / n_point 
    time_step_str = f"{time_step}ms"

    relative_residual = motor.calculation_data.convergence_settings.max_relative_residual
    relative_residual_str = f"{relative_residual}"
    
    setup = m3d.create_setup(name=setup_name, setup_type="Transient")
    setup.props["StopTime"] = stop_time_str
    setup.props["TimeStep"] = time_step_str
    setup.props["SaveFieldsType"] = "Every N Steps"
    setup.props["N Steps"] = "1"
    setup.props["Steps From"] = "0s"
    setup.props["Steps To"] = stop_time_str
    setup.props["NonlinearSolverResidual"] = relative_residual_str
    setup.props["ScalarPotential"] = "Second Order"
    setup.props["SmoothBHCurve"] = False
    setup.update()

    if motor.maxwell_export_option.solve_immediately :
        for setup_name in m3d.setup_names:
            m3d.analyze_setup(setup_name)