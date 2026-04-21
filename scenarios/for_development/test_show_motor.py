import paths
import math
pi = math.pi

from src.core.storage.core import motor_io 
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1

# Option
reload_motor = False
file_name = "motor_test_show_method"
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
    aft.require('geometry')
    aft.geometry.show()


    
if solve_semiFEM:
    aft.analysis_motor()
    aft.display()
    """
    if reload_motor is False:
        aft.data_processor.plot_flux_linkage(horizontal_axis="time")
        aft.data_processor.plot_back_emf(horizontal_axis="time")
        aft.data_processor.plot_back_emf_line(horizontal_axis="time")
        aft.data_processor.plot_current(horizontal_axis="time")
        aft.data_processor.plot_torque(horizontal_axis="time")
        aft.data_processor.plot_axial_force(horizontal_axis="time")
        aft.data_processor.plot_cogging_torque(horizontal_axis="time")
        aft.data_processor.plot_mechanical_power(horizontal_axis="time")
        aft.data_processor.plot_inductance_map()
    
    """

if export_maxwell:
    aft.export_to_rmxprt()
    aft.display()

# Visualizatn



aft.data_processor.compare_flux_linkage(horizontal_axis="time")
aft.data_processor.compare_back_emf(horizontal_axis="time")
aft.data_processor.compare_back_emf_line(horizontal_axis="time")
aft.data_processor.compare_torque(horizontal_axis="time")
aft.data_processor.compare_mechanical_power(horizontal_axis="time")
aft.data_processor.compare_cogging_torque(horizontal_axis="time")
aft.data_processor.compare_axial_force(horizontal_axis="time")


motor_io.save_motor(motor_obj=aft,filename= file_name)








