def set_reluctance_at_zero(reluctance_network):
    elements = reluctance_network.elements
    for element in elements.flat:
        element.set_reluctance_at_zero()
    
    if reluctance_network.system_variable == "magnetic_potential": 
        reluctance_network.magnetic_potential.data *= 0 
    else:
        reluctance_network.loop_flux.data *= 0 