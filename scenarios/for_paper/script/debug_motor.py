import paths
import math
import numpy as np 
import matplotlib.pyplot as plt
from src.core.storage.core.MotorIO import MotorIO
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
pi = math.pi
io = MotorIO()

# Initial setup
from src.core.ansys_maxwell.rmxprt.setup.init_window import init_window
init_window()

# Load motor
file_name = "motor_for_paper" 
aft = io.load(path=file_name)

# Option
solve_MBGRN = False
solve_FEM   = True
plot = True

aft.drive_data.i_rms = 10
aft.just_changed('drive')

aft.calculation_data.general_options.solve_cogging = False
aft.calculation_data.general_options.solve_standard = True
aft.calculation_data.general_options.solve_under_no_load = False
aft.maxwell_export_option.solver_option.solve_only_1_step =True
aft.calculation_data.general_options.n_point = 20
aft.calculation_data.convergence_settings.material_relax = 0.4
aft.calculation_data.convergence_settings.relaxation_decay = 0.5
aft.calculation_data.convergence_settings.max_relative_residual = 0.01 * 1e-2
aft.just_changed('calculation_data')

aft.maxwell_export_option.custom_option.mesh_setting.maximum_element_length = -1
# Motor properties
if plot: 
    aft.maxwell_export_option.solver_option.close_after_completed = False

# Solve
if solve_FEM: 
    aft.export_to_rmxprt()

if solve_MBGRN: 
    aft.analysis_motor()
    
print(aft.record.mesh_data_fem)

if plot: 
    dp = aft.data_processor
    dp.plot_solver_history(plot_relaxation_decay = False, step_index = [0,1,2])
    dp.plot_airgap_flux_density()
    dp.plot_airgap_flux_density_no_load()
    dp.plot_flux_linkage(horizontal_axis="time", show_fem=True, show_dq= False, show_all_phase= True)
    dp.plot_back_emf(horizontal_axis="time", show_fem=True, show_all_phases= True)
    dp.plot_torque(horizontal_axis="time", show_fem=True)
    dp.plot_mechanical_power(horizontal_axis="time", show_fem=True)
    dp.plot_cogging_torque(horizontal_axis="time", show_fem=True, revert = False, num_periods= 5)
    dp.plot_axial_force(horizontal_axis="time", show_fem=True)

    aft.display()




