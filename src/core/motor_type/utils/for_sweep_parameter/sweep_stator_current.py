import numpy as np

def sweep_stator_current(motor):
    print("\033[94mIn function sweep_stator_current.\033[0m")
    print("\033[94m{\033[0m")

    sweep_config = motor.calculation_data.sweep_stator_current
    current_min = sweep_config.current_min
    current_max = sweep_config.current_max
    delta_current = sweep_config.delta_current
    
    # Tự động tính toán dải dòng điện dựa trên current_min, current_max và delta_current
    target_stator_currents = np.arange(current_min, current_max + delta_current / 2.0, delta_current)
    number_of_division = len(target_stator_currents)

    print("\033[94mIn function sweep_stator_current: Initializing a new simulation array from scratch.\033[0m")
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
            print(f"\033[94mIn function sweep_stator_current: Skipping stator current point: {stator_current} A (Column {col_idx}) - Already calculated.\033[0m")
            continue

        print(f"\033[94mIn function sweep_stator_current: Simulating stator current point: {stator_current} A (Column {col_idx})\033[0m")

        motor.drive_data.i_rms = stator_current
        motor.just_changed('drive')

        # Khởi tạo giá trị mặc định cho vòng lặp hiện tại
        mbgrn_power = -999.0
        fem_power = -999.0

        # 1. LUÔN GIẢI FEM TRƯỚC
        motor.export_to_rmxprt()
        
        # 2. GIẢI MBGRN SAU
        motor.analysis_motor()
            
        # 3. ĐỌC DỮ LIỆU KẾT QUẢ ĐÃ GIẢI
        fem_power = motor.record.average_mechanical_power_fem
        mbgrn_power = motor.record.average_mechanical_power

        current_array[0, col_idx] = mbgrn_power
        current_array[1, col_idx] = fem_power

        motor.record.power_at_varying_current = current_array.copy()

    motor.drive_data.i_rms = motor.drive_data.i_rms_draft
    motor.just_changed('drive')

    print("\033[94mIn function sweep_stator_current: Completed all simulation points.\033[0m")
    print("\033[94m}\033[0m")
    print("\033[94m\033[0m")

    return current_array