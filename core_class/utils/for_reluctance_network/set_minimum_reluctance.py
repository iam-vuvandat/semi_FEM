def set_minimum_reluctance(reluctance_network):
    elements = reluctance_network.elements
    for element in elements.flat:
        element.set_reluctance_minimum()