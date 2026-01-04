from tqdm import tqdm

def update_reluctance_network(reluctance_network, 
                              magnetic_potential=None,
                              winding_current=None,
                              material_relaxation_factor = 1.0,
                              delta_mu_max=-1,
                              debug=False):
    
    reluctance_network.magnetic_potential = magnetic_potential
    reluctance_network.winding_current = winding_current

    iterator = tqdm(reluctance_network.elements.flat, 
                    total=reluctance_network.elements.size, 
                    desc="Updating Network", 
                    disable=not debug)

    for element in iterator:
        if element is not None:
            element.update_element(magnetic_potential=magnetic_potential,
                                   winding_current=winding_current,
                                   material_relaxation_factor = material_relaxation_factor,
                                   delta_mu_max= delta_mu_max)