from typing import Any
from src.core.core_class.utils.for_reluctance_network.create_magnetic_potential import create_magnetic_potential
from src.core.core_class.utils.for_reluctance_network.create_loop_flux import create_loop_flux
from dataclasses import dataclass
from src.core.core_class.models.LoopFlux import LoopFLux

@dataclass
class SystemVariable:
    loop_flux: Any
    magnetic_potential: Any

def create_system_variable(reluctance_network):

    loop_flux = None
    magnetic_potential = None

   
    magnetic_potential =  create_magnetic_potential(reluctance_network= reluctance_network)
    
    return SystemVariable(loop_flux = loop_flux,
                          magnetic_potential = magnetic_potential)