import numpy as np

def sweep_stator_current(motor):
    sweep_config = motor.calculation_data.sweep_stator_current
    current_range = (sweep_config.current_min, sweep_config.current_max)
    number_of_division = sweep_config.n_point
    
    target_stator_currents = np.linspace(current_range[0], current_range[1], number_of_division)

    has_old_data = hasattr(motor.record, "power_at_varying_current") and motor.record.power_at_varying_current is not None

    if sweep_config.clear_history or not has_old_data:
        print("Initializing a new simulation array from scratch.")
        power_placeholders = np.full((2, number_of_division), -999.0)
        current_array = np.vstack([power_placeholders, target_stator_currents])
        motor.record.power_at_varying_current = current_array
    else:
        print("Reading existing simulation data from history.")
        current_array = motor.record.power_at_varying_current
        
        if current_array.shape[0] != 3 or current_array.shape[1] != number_of_division or not np.allclose(current_array[-1], target_stator_currents):
            print("Warning: Target currents or division mismatch. Reinitializing array to match new config.")
            power_placeholders = np.full((2, number_of_division), -999.0)
            current_array = np.vstack([power_placeholders, target_stator_currents])
            motor.record.power_at_varying_current = current_array

    motor.drive_data.i_rms_draft = motor.drive_data.i_rms

    motor.calculation_data.general_options.solve_standard = True
    motor.calculation_data.general_options.solve_cogging  = False
    motor.calculation_data.general_options.solve_only_1_step = False

    motor.maxwell_export_option.solver_option.close_after_completed = True

    for col_idx, stator_current in enumerate(current_array[-1]):
        if current_array[0, col_idx] != -999.0 and current_array[1, col_idx] != -999.0:
            print(f"Skipping stator current point: {stator_current} A (Column {col_idx}) - Already calculated.")
            continue

        print(f"Simulating stator current point: {stator_current} A (Column {col_idx})")

        motor.drive_data.i_rms = stator_current
        motor.just_changed('drive')

        motor.analysis_motor()
        motor.export_to_rmxprt()

        mbgrn_power = motor.record.average_mechanical_power
        fem_power = motor.record.average_mechanical_power_fem

        current_array[0, col_idx] = mbgrn_power
        current_array[1, col_idx] = fem_power

        motor.record.power_at_varying_current = current_array

    motor.drive_data.i_rms = motor.drive_data.i_rms_draft
    motor.just_changed('drive')

    return current_array