import paths
import math
from src.core.storage.core.MotorIO import MotorIO
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1

pi = math.pi

# Initialize new MotorIO instance
io = MotorIO()

# Options
reload_motor = True
file_name = "motor_test"
export_maxwell = True
solve_semiFEM = True

if reload_motor:
    export_maxwell = False
    solve_semiFEM = False
    # Use the new load method
    aft = io.load(path=file_name)
else:
    aft = AxialFluxMotorType1()
    aft.geometry_data.stator.slot_number = 30
    aft.geometry_data.rotor.pole_number = 20
    aft.just_changed('geometry')

    aft.calculation_data.general_options.n_point = 50
    aft.calculation_data.general_options.solve_cogging = True
    aft.maxwell_export_option.solver_option.solve_immediately = True
    aft.calculation_data.general_options.solve_only_1_step = False
    aft.just_changed('calculation_data')


if export_maxwell:
    aft.export_to_rmxprt()
    

if solve_semiFEM:
    aft.analysis_motor()
    

dp = aft.data_processor

dp.plot_flux_linkage(horizontal_axis="time", show_fem=True, show_dq= True, show_all_phase= True)
dp.plot_back_emf(horizontal_axis="time", show_fem=True, show_all_phases= True)
dp.plot_torque(horizontal_axis="time", show_fem=True)
dp.plot_mechanical_power(horizontal_axis="time", show_fem=True)

aft.record.cogging_fem[0,:] *= 1/1000

dp.plot_cogging_torque(horizontal_axis="time", show_fem=True, revert = False)

print(aft.record.axial_force_fem)
aft.record.axial_force_fem[0,:] *= 1000
dp.plot_axial_force(horizontal_axis="time", show_fem=True)

if not reload_motor:
    # Use the new save method
    io.save(motor=aft, path=file_name)