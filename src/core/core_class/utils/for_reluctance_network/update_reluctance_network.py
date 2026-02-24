from tqdm import tqdm

def update_reluctance_network(reluctance_network, 
                              loop_flux = None,
                              magnetic_potential=None,
                              winding_current=None,
                              material_relaxation_factor = 1.0,
                              delta_mu_max=-1,
                              debug=False):
    
    if loop_flux is not None:
        reluctance_network.loop_flux = loop_flux
    
    if magnetic_potential is not None:
        reluctance_network.magnetic_potential = magnetic_potential
        
    if winding_current is not None:
        reluctance_network.winding_current = winding_current

    iterator = tqdm(reluctance_network.elements.flat, 
                    total=reluctance_network.elements.size, 
                    desc="Updating Network", 
                    disable=not debug)

    for element in iterator:
        if element is not None:
            element.update_element(magnetic_potential=magnetic_potential,
                                   loop_flux = loop_flux,
                                   winding_current=winding_current,
                                   material_relaxation_factor = material_relaxation_factor,
                                   delta_mu_max= delta_mu_max)