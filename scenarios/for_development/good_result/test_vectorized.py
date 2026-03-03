import paths

from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1

aft = AxialFluxMotorType1()
aft.require("reluctance_network")