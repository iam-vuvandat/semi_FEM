import paths
import math
pi = math.pi


from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1


aft = AxialFluxMotorType1()
aft.geometry_data.stator.slot_number = 30
aft.geometry_data.rotor.pole_number = 20
aft.just_changed('geometry_data')

aft.calculation_data.general_options.solve_only_1_step = True
aft.just_changed('calculation_data')



aft.analysis_motor()
aft.display()
    