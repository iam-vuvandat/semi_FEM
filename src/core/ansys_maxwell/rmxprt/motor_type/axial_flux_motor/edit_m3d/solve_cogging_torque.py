import math
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.edit_excitation import edit_excitation
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.cogging_torque_export import cogging_torque_export
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.calculate_electrical_frequency import calculate_electrical_frequency
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.export_solution_data import export_solution_data


def solve_cogging_torque(m3d=None, motor=None):
    if motor.calculation_data.general_options.solve_cogging:
        setup_name = "Setup1"
        if setup_name in m3d.setup_names:
            m3d.delete_setup(setup_name)

        edit_excitation(m3d=m3d, motor=motor, disable_excitation=True)

        motor.require("mechanical")

        shaft_speed = motor.mechanical_data.shaft_speed * (2 * math.pi / 60)
        theta_sweep = motor.mechanical.cogging_period_mech
        
        stop_time = (theta_sweep / shaft_speed) * 1000

        n_point = motor.calculation_data.general_options.n_point
        time_step = stop_time / n_point

        stop_time -=time_step
        time_step_str = f"{time_step}ms"

        stop_time_str = f"{stop_time}ms"

        if motor.maxwell_export_option.solver_option.solve_only_1_step:
            time_step_str = stop_time_str

        relative_residual_str = str(motor.calculation_data.convergence_settings.max_relative_residual)

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
        setup.props["FastReachSteadyState"] = False
        pole_pairs = motor.geometry_data.rotor.pole_number / 2 
        speed_rpm = motor.mechanical_data.shaft_speed

        frequency_string = calculate_electrical_frequency(rated_speed_rpm= speed_rpm, poles= pole_pairs, return_string= True)

        setup.props["FrequencyOfAddedVoltageSource"]= frequency_string
        setup.props["IsGeneralTransient"] = True


        setup.update()

        m3d.oproject.Save()

        if motor.maxwell_export_option.solver_option.solve_immediately:
            m3d.analyze_setup(setup_name)
            cogging_torque_export(motor=motor, m3d=m3d)

        print(f"\033[92msolve_cogging_torque return: True\033[0m")
        export_solution_data(m3d = m3d, motor = motor)
        return True
    else:
        return False
    

