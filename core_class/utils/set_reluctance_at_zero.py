def set_reluctance_at_zero(reluctance_network):
    elements = reluctance_network.elements
    for element in elements.flat:
        element.set_reluctance_at_zero()


