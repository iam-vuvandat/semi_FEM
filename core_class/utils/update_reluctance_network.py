from tqdm import tqdm

def update_reluctance_network(reluctance_network, 
                              magnetic_potential=None,
                              winding_current=None,
                              debug=True):
    
    reluctance_network.magnetic_potential = magnetic_potential
    reluctance_network.winding_current = winding_current

    iterator = tqdm(reluctance_network.elements.flat, 
                    total=reluctance_network.elements.size, 
                    desc="Updating Network", 
                    disable=not debug)

    for element in iterator:
        if element is not None:
            element.update_element(magnetic_potential=magnetic_potential,
                                   winding_current=winding_current)