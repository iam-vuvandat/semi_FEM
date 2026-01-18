from src.core.core_class.models.LoopFlux import LoopFLux

def create_loop_flux(reluctance_network):
    return LoopFLux(reluctance_network= reluctance_network)