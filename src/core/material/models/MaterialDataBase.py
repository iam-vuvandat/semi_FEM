from src.core.material.models.Air import Air
from src.core.material.models.Iron import Iron
from src.core.material.models.Magnet import Magnet

class MaterialDataBase:
    def __init__(self, air="default", magnet_type= "NdFe30", iron_type="steel_1008"):
        self.air = Air(air)
        self.magnet = Magnet(magnet_type)
        self.iron = Iron(iron_type)

