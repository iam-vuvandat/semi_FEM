import paths
import math
import numpy as np 
import matplotlib.pyplot as plt
from src.core.storage.core.MotorIO import MotorIO
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
pi = math.pi
io = MotorIO()

# initial setup
from src.core.ansys_maxwell.rmxprt.setup.init_window import init_window
init_window()

# Option
solve = True
current_range = (0,18) #ampere
number_of_division = 10
file_name = "motor_for_paper" 
aft = io.load(path=file_name)

# Plot status flag
should_plot = False

if solve:
    # data array: [MBGRN power; FEM power; Stator current]
    current_array = np.vstack([np.zeros((2, number_of_division)), np.linspace(current_range[0], current_range[1], number_of_division)])

    # setting 
    aft.calculation_data.general_options.solve_standard = True
    aft.calculation_data.general_options.solve_cogging  = False
    aft.calculation_data.general_options.solve_only_1_step = False
    aft.calculation_data.general_options.n_point = 15
    aft.calculation_data.convergence_settings.material_relax = 0.15
    aft.calculation_data.convergence_settings.max_relative_residual = 0.5 * 1e-2
    aft.just_changed('calculation_data')

    aft.maxwell_export_option.custom_option.mesh_setting.length_band_element_length = -1
    aft.maxwell_export_option.custom_option.mesh_setting.length_coil_element_length = -1
    aft.maxwell_export_option.custom_option.mesh_setting.length_mag_element_length = -1
    aft.maxwell_export_option.custom_option.mesh_setting.length_main_element_length = -1
    aft.maxwell_export_option.custom_option.mesh_setting.length_region_element_length = -1
    aft.maxwell_export_option.solver_option.close_after_completed = True

    for col_idx, stator_current in enumerate(current_array[-1]):
        # Print progress status in yellow
        print(f"\033[93m[Processing] Solving current step {col_idx + 1}/{number_of_division} (Current: {stator_current:.2f} A)...\033[0m")

        # Setup stator current
        aft.drive_data.i_rms = stator_current
        aft.just_changed('drive')

        # Solve
        aft.analysis_motor()
        aft.export_to_rmxprt()

        # export result
        mbgrn_power = aft.record.average_mechanical_power
        fem_power = aft.record.average_mechanical_power_fem

        # Save data to corresponding row and column
        current_array[0, col_idx] = mbgrn_power
        current_array[1, col_idx] = fem_power

        # Overwrite data
        aft2 = io.load(path=file_name)
        aft2.record.power_at_varying_current = current_array
        io.save(motor=aft2, path=file_name)
        should_plot = True
else:
    # Load existing data from file for plotting if solve is False
    if hasattr(aft.record, 'power_at_varying_current') and aft.record.power_at_varying_current is not None:
        current_array = aft.record.power_at_varying_current
        should_plot = True
    else:
        print("Không có dữ liệu power_at_varying_current để vẽ đồ thị.")

# Execute plotting if condition is met
if should_plot:
    stator_current_data = current_array[2]
    mbgrn_power_data = current_array[0]
    fem_power_data = current_array[1]

    plt.figure(figsize=(8, 5))
    plt.plot(stator_current_data, mbgrn_power_data, 'b-o', label='MBGRN Power')
    plt.plot(stator_current_data, fem_power_data, 'r-x', label='FEM Power')
    plt.xlabel('Stator Current (A)')
    plt.ylabel('Mechanical Power (W)')
    plt.grid(True)
    plt.legend()
    plt.show()
