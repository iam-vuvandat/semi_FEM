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
solve = False
clear_data = False
current_range = (0, 20) #ampere
number_of_division = 10
file_name = "motor_for_paper" 
aft = io.load(path=file_name)

should_plot = False
target_stator_currents = np.linspace(current_range[0], current_range[1], number_of_division)

if solve:
    # Check if historical simulation data exists in the file
    recorded_data_exists = hasattr(aft.record, 'power_at_varying_current') and aft.record.power_at_varying_current is not None

    if recorded_data_exists and not clear_data:
        print("Historical simulation data detected. Checking array structure...")
        old_array = aft.record.power_at_varying_current
        
        # Check if the number of elements matches current configuration
        if old_array.shape == (3, number_of_division):
            print("Array structure matches. Proceeding with missing simulation points.")
            current_array = old_array
        else:
            print(f"WARNING: Historical array has shape {old_array.shape}, which differs from current configuration (3, {number_of_division}).")
            print("For data safety, the program keeps the old array for plotting/analysis and will NOT overwrite it.")
            current_array = old_array
            solve = False  # Lock simulation to protect old data
    else:
        if clear_data:
            print("Request clear_data = True. Initializing a new simulation array from scratch.")
        else:
            print("No historical data found in file. Initializing a new simulation array from scratch.")
        current_array = np.vstack([np.zeros((2, number_of_division)), target_stator_currents])

    # Run simulation only if safety checks pass and solver is not locked
    if solve:
        # setting 
        aft.calculation_data.general_options.solve_standard = True
        aft.calculation_data.general_options.solve_cogging  = False
        aft.calculation_data.general_options.solve_only_1_step = False

        aft.maxwell_export_option.solver_option.close_after_completed = True

        # Sweep through points
        for col_idx, stator_current in enumerate(current_array[-1]):
            # If current is 0.0 A and resuming from historical data, skip solving (default power is 0)
            if stator_current == 0 and recorded_data_exists:
                continue

            # For non-zero points, if already solved (power is non-zero), skip solving
            if stator_current != 0:
                if current_array[0, col_idx] != 0 or current_array[1, col_idx] != 0:
                    continue

            print(f"Simulating stator current point: {stator_current} A (Column {col_idx})")

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

            # Overwrite data continuously to prevent data loss if interrupted
            aft2 = io.load(path=file_name)
            aft2.record.power_at_varying_current = current_array
            io.save(motor=aft2, path=file_name)

        should_plot = True
    else:
        should_plot = True
else:
    # If solve is False, load existing data from file for plotting
    if hasattr(aft.record, 'power_at_varying_current') and aft.record.power_at_varying_current is not None:
        current_array = aft.record.power_at_varying_current
        should_plot = True
    else:
        print("No power_at_varying_current data available for plotting.")

# Execute plotting
if should_plot:
    stator_current_data = current_array[2]
    mbgrn_power_data = current_array[0]
    fem_power_data = current_array[1]

    # Calculate first derivative (dP/dI) using numerical gradient
    dP_dI_mbgrn = np.gradient(mbgrn_power_data, stator_current_data)
    dP_dI_fem = np.gradient(fem_power_data, stator_current_data)

    # Create subplots: 2 rows, 1 column
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 9), sharex=True)

    # Plot 1: Mechanical Power vs Stator Current
    ax1.plot(stator_current_data, mbgrn_power_data, 'b-o', label='MBGRN Power')
    ax1.plot(stator_current_data, fem_power_data, 'r-x', label='FEM Power')
    ax1.set_ylabel('Mechanical Power (W)')
    ax1.set_title('Saturation Analysis: Mechanical Power and Its Derivative')
    ax1.grid(True)
    ax1.legend()

    # Plot 2: Derivative dP/dI vs Stator Current
    ax2.plot(stator_current_data, dP_dI_mbgrn, 'b--o', label='d(Power)/d(Current) - MBGRN')
    ax2.plot(stator_current_data, dP_dI_fem, 'r--x', label='d(Power)/d(Current) - FEM')
    ax2.set_xlabel('Stator Current (A)')
    ax2.set_ylabel('dP/dI (W/A)')
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()