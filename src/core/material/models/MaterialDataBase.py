import math
import numpy as np
from src.core.material.models.Iron import Iron
from src.core.material.models.Magnet import Magnet
from src.core.material.utils.smooth_BH_curve import smooth_BH_curve
from src.core.material.utils.staircase_permeability import staircase_permeability
from src.core.material.utils.continuous_permeability import continuous_permeability


PI = math.pi

class Air:
    def __init__(self, name="default"):
        self.name = name
        self.relative_permeance = 1.

class MaterialDataBase:
    def __init__(self, air="default", magnet_type= "NdFe30", iron_type="steel_1008"):
        self.air = Air(air)
        self.magnet = Magnet(magnet_type)
        self.iron = Iron(iron_type)

    def staircase_permeability(self,num_step = 10):
        staircase_permeability(iron=self.iron, 
                               num_steps= num_step)
        
    def continuous_permeability(self):
        continuous_permeability(iron = self.iron)
        