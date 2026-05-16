import paths
import math
from src.core.storage.core.MotorIO import MotorIO
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
pi = math.pi
io = MotorIO()

# initial setup
from src.core.ansys_maxwell.rmxprt.setup.init_window import init_window
init_window()

file_name = "motor_for_paper" 
aft = io.load(path=file_name)
aft.calculation_data.general_options.solve_standard = True
aft.calculation_data.general_options.solve_cogging  = False
aft.calculation_data.general_options.solve_only_1_step = True

# Option
visualization_under_no_load = False
if visualization_under_no_load:
    aft.drive_data.i_rms = 0.0

# Visualization for Reluctance Network
aft.analysis_motor()
aft.display()


