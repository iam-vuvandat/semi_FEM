import paths
import math
pi = math.pi

from src.core.storage.core import motor_io 
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1

# Option
reload_motor = False
file_name = "motor_test"
export_maxwell = True
solve_semiFEM = True

if reload_motor:
    export_maxwell = False
    solve_semiFEM = False
    aft = motor_io.load_motor(filename = file_name)
else:
    aft = AxialFluxMotorType1()
    aft.geometry_data.stator.slot_number = 30
    aft.geometry_data.rotor.pole_number = 20
    aft.just_changed('geometry')

    aft.calculation_data.general_options.n_point = 3
    aft.maxwell_export_option.solver_option.solve_immediately = True
    aft.calculation_data.general_options.solve_only_1_step = False
    aft.just_changed('calculation_data')


if export_maxwell:
    aft.export_to_rmxprt()
    pass

if solve_semiFEM:
    #aft.analysis_motor()
    pass



dp = aft.data_processor

dp.plot_flux_linkage(horizontal_axis="time", show_fem=True, show_dq= True, show_all_phase= True)
dp.plot_back_emf(horizontal_axis="time", show_fem=True, show_all_phases= True)
dp.plot_torque(horizontal_axis="time", show_fem=True)
dp.plot_mechanical_power(horizontal_axis="time", show_fem=True)
dp.plot_cogging_torque(horizontal_axis="time", show_fem=True)
dp.plot_axial_force(horizontal_axis="time", show_fem=True)

if not reload_motor:
    motor_io.save_motor(motor_obj=aft,filename= file_name)