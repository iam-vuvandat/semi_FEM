def update_for_vectorized_elements(vectorized_elements,
                               magnetic_potential = None,
                               winding_current = None,
                               update_for_magnetic_potential = False,
                               update_for_winding_current =False,
                               material_relaxation_factor =1.0,
                               delta_mu_max = -1):
    
    if update_for_magnetic_potential:
        vectorized_elements.magnetic_potential = magnetic_potential.data.ravel(order = 'F')
        vectorized_elements.update_flux_direct()
        vectorized_elements.update_flux_density_direct()
        vectorized_elements.update_flux_density_average()
        vectorized_elements.update_relative_permeability(material_relaxation_factor = material_relaxation_factor,
                                                         delta_mu_max=delta_mu_max)
        
        vectorized_elements.update_vectorized_reluctance()

    if update_for_winding_current:
        vectorized_elements.winding_current = winding_current
        vectorized_elements.update_winding_source()
        vectorized_elements.update_magnetic_source()

    