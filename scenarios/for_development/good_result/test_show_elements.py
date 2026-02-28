from matplotlib.pylab import True_
from sympy import true

import paths
import numpy as np
import matplotlib.pyplot as plt
import math

from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io

RE_CREATE_MOTOR = True
FILENAME        = "AFT_Motor_Optimization"

aft = AxialFluxMotorType1()
aft.analysis_motor()


