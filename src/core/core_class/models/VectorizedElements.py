import numpy as np
from src.core.core_class.utils.for_vectorized_elements.create_vectorized_elements import create_vectorized_elements
from src.core.core_class.utils.for_vectorized_elements.update_permeability import update_permeability
from src.core.core_class.utils.for_vectorized_elements.update_reluctance import update_reluctance
from src.core.core_class.utils.for_vectorized_elements.update_vectorized_flux_direct import update_vectorized_flux_direct
from src.core.core_class.utils.for_vectorized_elements.update_vectorized_flux_density_direct import update_vectorized_flux_density
from src.core.core_class.utils.for_vectorized_elements.update_vectorized_flux_density_average import update_vectorized_flux_density_average
from src.core.core_class.utils.for_vectorized_elements.update_winding_current import reload_winding_current
from src.core.core_class.utils.for_vectorized_elements.update_vectorized_winding_source import update_vectorized_winding_source
from src.core.core_class.utils.for_vectorized_elements.update_vectorized_magnetic_source import update_vectorized_magnetic_source
from src.core.core_class.utils.for_vectorized_elements.update_vectorized_elements import update_for_vectorized_elements
from src.core.core_class.utils.for_vectorized_elements.rotate_for_vectorized_elements import rotate_for_vectorized_elements


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
        update_vectorized_winding_source(vectorized_elements= self)

    def update_magnetic_source(self):
        update_vectorized_magnetic_source(vectorized_elements= self)

    def update_vectorized_elements(self,
                                   magnetic_potential = None,
                                   winding_current = None,
                                   update_for_magnetic_potential = False,
                                   update_for_winding_current =False,
                                   material_relaxation_factor =1.0,
                                   delta_mu_max = -1):
        
        update_for_vectorized_elements(vectorized_elements= self,
                                       magnetic_potential= magnetic_potential,
                                       winding_current= winding_current,
                                       update_for_magnetic_potential= update_for_magnetic_potential,
                                       update_for_winding_current= update_for_winding_current,
                                       material_relaxation_factor= material_relaxation_factor,
                                       delta_mu_max= delta_mu_max
                                       )
        
    def rotate_vectorized_elements(self,
                                   z_indices = [0,1,2],
                                   n_step = 1):
        rotate_for_vectorized_elements(vectorized_elements=self,
                                       z_indices= z_indices,
                                       n_step= n_step)
    
    