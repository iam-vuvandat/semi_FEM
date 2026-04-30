import math

from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.flux_linkage_export import flux_linkage_export
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.torque_export import torque_export
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.axial_force_export import axial_force_export
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.calculate_electrical_frequency import calculate_electrical_frequency
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.export_solution_data import export_solution_data


def solve_standard_step(m3d, motor):
    
    setup_name = "Setup1"
    
    # 1. Kiem tra va xoa setup cu neu ton tai
    if setup_name in m3d.setup_names:
        m3d.delete_setup(setup_name)

    motor.require("mechanical")

    

    oModule = m3d.odesign.GetModule("AnalysisSetup")

    # 2. Trich xuat va tinh toan cac thong so thoi gian
    # Chuyen doi toc do shaft tu rpm sang rad/s
    shaft_speed = motor.mechanical_data.shaft_speed 
    shaft_speed_rad = shaft_speed * (2 * math.pi / 60)

    # Tinh toan goc quet dua tren he so doi xung
    symmetry_factor = motor.mechanical.symmetry_factor 
    theta_sweep = (2 * math.pi) / symmetry_factor 

    # Tinh StopTime va TimeStep (don vi ms)
    stop_time_ms = (theta_sweep / shaft_speed_rad) * 1000
    n_point = motor.calculation_data.general_options.n_point 
    
    # Mac dinh time_step
    time_step_ms = stop_time_ms / n_point 
    stop_time_ms -= time_step_ms

    # Truong hop dac biet: chi giai 1 buoc
    if motor.maxwell_export_option.solver_option.solve_only_1_step: 
        time_step_ms = stop_time_ms

    stop_time_str = f"{stop_time_ms}ms"
    time_step_str = f"{time_step_ms}ms"
    
    # Lay sai so hoi tu
    relative_residual = motor.calculation_data.convergence_settings.max_relative_residual
    relative_residual_str = str(relative_residual)

    # 3. Cau hinh Setup1 (Su dung oModule.EditSetup hoac m3d.create_setup)
    # De dam bao tinh tuong thich voi kich ban recorded, ta dung Edit hoac kieu dictionary props
    setup = m3d.create_setup(name=setup_name, setup_type="Transient")
    setup.props["StopTime"] = stop_time_str
    setup.props["TimeStep"] = time_step_str
    setup.props["NonlinearSolverResidual"] = relative_residual_str
    setup.props["ScalarPotential"] = "Second Order"
    setup.props["SmoothBHCurve"] = False
    setup.props["SaveFieldsType"] = "Every N Steps"
    setup.props["N Steps"] = "1"
    setup.props["Steps From"] = "0s"
    setup.props["Steps To"] = stop_time_str
    
    # Bo sung cac thong so tu kịch bản recorded 2025.2
    setup.props["FastReachSteadyState"] = True
    setup.props["AutoDetectSteadyState"] = True
    setup.props["OutputPerObjectCoreLoss"] = True

    pole_pairs = motor.geometry_data.rotor.pole_number / 2 
    speed_rpm = motor.mechanical_data.shaft_speed

    frequency_string = calculate_electrical_frequency(rated_speed_rpm= speed_rpm, poles= pole_pairs, return_string= True)

    setup.props["FrequencyOfAddedVoltageSource"]= frequency_string
    setup.props["IsGeneralTransient"] = True
    
    
    setup.update()

    # 4. Luu project
    m3d.oproject.Save()

    # 5. Giai va xuat du lieu neu duoc yeu cau
    if motor.maxwell_export_option.solver_option.solve_immediately:
        print(f"Starting analysis for {setup_name}...")
        m3d.analyze_setup(setup_name)
        
        print("Flux linkage export starting")
        flux_linkage_export(motor=motor, m3d=m3d)
        
        print("Torque export starting")
        torque_export(motor=motor, m3d=m3d)

        print("Axial force export starting")
        axial_force_export(motor = motor, m3d = m3d)
        
        print("\033[92mExport data successfully\033[0m")

    print(f"\033[92msolve_standard_step return: True\033[0m")

    export_solution_data(m3d = m3d, motor = motor)
    return True