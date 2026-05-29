import paths
import math
import numpy as np 
import matplotlib.pyplot as plt
from src.core.storage.core.MotorIO import MotorIO

pi = math.pi
io = MotorIO()

from src.core.ansys_maxwell.rmxprt.setup.init_window import init_window
init_window()

solve = False
clear_data = False
file_name = "motor_for_paper" 
aft = io.load(path=file_name)

should_plot = False

if solve:
    aft.calculation_data.sweep_stator_current.clear_history = clear_data

    # Execute via the object method instead of an external function import
    current_array = aft.sweep_stator_current(file_name=file_name)
    
    # Final safe confirmation write step
    aft2 = io.load(path=file_name)
    aft2.record.power_at_varying_current = current_array
    aft2.drive_data.i_rms = aft.drive_data.i_rms_draft
    io.save(motor=aft2, path=file_name)
    should_plot = True
else:
    if hasattr(aft.record, 'power_at_varying_current') and aft.record.power_at_varying_current is not None:
        should_plot = True
    else:
        print("No power_at_varying_current data available for plotting.")

if should_plot:
    print("Invoking motor.data_processor to generate academic plots...")
    aft.data_processor.plot_power_at_varying_current(plot=True)