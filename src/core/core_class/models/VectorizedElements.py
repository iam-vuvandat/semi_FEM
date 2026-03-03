import numpy as np
from src.core.core_class.utils.for_vectorized_elements.create_vectorized_elements import create_vectorized_elements
from src.core.core_class.utils.for_vectorized_elements.update_permeability import update_permeability
from src.core.core_class.utils.for_vectorized_elements.update_reluctance import update_reluctance
from src.core.core_class.utils.for_vectorized_elements.update_vectorized_flux_direct import update_vectorized_flux_direct
from src.core.core_class.utils.for_vectorized_elements.update_vectorized_flux_density_direct import update_vectorized_flux_density
from src.core.core_class.utils.for_vectorized_elements.update_vectorized_flux_density_average import update_vectorized_flux_density_average
from src.core.core_class.utils.for_vectorized_elements.update_winding_current import reload_winding_current

class VectorizedElements:
    def __init__(self, reluctance_network):
        self.reluctance_network = reluctance_network
        self.init_vectorized_elements()
        
    def init_vectorized_elements(self):
        create_vectorized_elements(vectorized_elements=self)
    
    def update_relative_permeability(self, material_relaxation_factor=1.0, delta_mu_max=-1):
        update_permeability(
            vectorized_elements=self, 
            material_relaxation_factor=material_relaxation_factor, 
            delta_mu_max=delta_mu_max
        )
    
    def update_vectorized_reluctance(self):
        update_reluctance(vectorized_elements= self)

    def update_flux_direct(self):
        update_vectorized_flux_direct(vectorized_elements= self)    

    def update_flux_density_direct(self):
        update_vectorized_flux_density(vectorized_elements=self)

    def update_flux_density_average(self):
        update_vectorized_flux_density_average(vectorized_elements=self)
    
    def update_winding_current(self):
        reload_winding_current(vectorized_elements=self)

    def update_winding_source(self):
        
