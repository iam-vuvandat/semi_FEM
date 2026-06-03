import paths
import math
from src.core.storage.core.MotorIO import MotorIO

pi = math.pi
io = MotorIO()

from src.core.ansys_maxwell.rmxprt.setup.init_window import init_window
init_window()

solve = True
clear_data = False
file_name = "motor_for_paper" 
aft = io.load(path=file_name)

if solve: 
    # use default mesh setting
    aft.maxwell_export_option.custom_option.mesh_setting.length_band_element_length = -1
    aft.maxwell_export_option.custom_option.mesh_setting.length_coil_element_length = -1
    aft.maxwell_export_option.custom_option.mesh_setting.length_mag_element_length = -1
    aft.maxwell_export_option.custom_option.mesh_setting.length_main_element_length = -1
    aft.maxwell_export_option.custom_option.mesh_setting.length_region_element_length = -1

    # modify solver option

    aft.calculation_data.convergence_settings.max_iteration = 46
    aft.calculation_data.convergence_settings.max_relative_residual = 0.5 * 1e-2
    aft.calculation_data.convergence_settings.material_relax = 0.2
    aft.calculation_data.convergence_settings.damping_factor = 1.0
    aft.calculation_data.convergence_settings.relaxation_decay = 0.6

    aft.calculation_data.general_options.n_point = 20
    aft.calculation_data.general_options.solve_cogging = False
    aft.calculation_data.general_options.solve_standard = True
    aft.calculation_data.general_options.solve_under_no_load = False
    aft.calculation_data.general_options.solve_on_load = True

    aft.calculation_data.sweep_stator_current.current_min = 0.0 
    aft.calculation_data.sweep_stator_current.current_max = 20.0
    aft.calculation_data.sweep_stator_current.delta_current = 2
    aft.just_changed('calculation_data')

    aft.sweep_stator_current()
    aft1  = io.load(path=file_name)
    aft1.record = aft.record
    io.save(motor = aft1, path= file_name)

else: 
    pass

aft.data_processor.plot_power_at_varying_current()

