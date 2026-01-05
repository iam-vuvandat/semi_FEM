def set_reluctance_at_zero(reluctance_network):
    elements = reluctance_network.elements
    for element in elements.flat:
        element.set_reluctance_at_zero()

    reluctance_network.magnetic_potential.data *= 0 
    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
