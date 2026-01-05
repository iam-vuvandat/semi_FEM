from material.core.lookup_BH_curve import lookup_BH_curve

def set_element_reluctance_at_zero(element):
    material_database = element.material_database
    permeability_at_zero = lookup_BH_curve(B_input= 0.0,
                                           material_database= material_database).mu_r
    
    if element.material == "iron":
        element.reluctance = element.vacuum_reluctance * (1/permeability_at_zero)