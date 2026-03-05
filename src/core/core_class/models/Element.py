from src.core.core_class.utils.for_element.find_vacuum_reluctance import find_vacuum_reluctance
from src.core.core_class.utils.for_element.extract_element_info import extract_element_info
from src.core.core_class.utils.for_element.find_element_dimension import find_element_dimension
from src.core.core_class.utils.for_element.find_minimum_reluctance import find_minimum_reluctance
from src.core.core_class.utils.for_element.find_magnet_source import find_magnet_source
from src.core.core_class.utils.for_element.find_element_segment_dimension_ratio import find_element_segment_dimension_ratio
from src.core.core_class.utils.for_element.find_winding_source import find_winding_source
from src.core.core_class.utils.for_element.find_branch_magnetic_source import find_branch_magnetic_source
from src.core.core_class.utils.for_element.find_flux_direct import find_flux_direct
from src.core.core_class.utils.for_element.get_neighbor_elements_position import get_neighbor_elements_position
from src.core.core_class.utils.for_element.find_neighbor_elements import find_neighbor_elements
from src.core.core_class.utils.for_element.find_flux_density import find_flux_density
from src.core.core_class.utils.for_element.find_relative_permeability import find_relative_permeability
from src.core.core_class.utils.for_element.find_reluctance_updated import find_reluctance_updated
from src.core.core_class.utils.for_element.find_own_magnetic_potential import find_own_magnetic_potential
from src.core.core_class.utils.for_element.find_flat_position import find_flat_position
from src.core.core_class.utils.for_element.set_element_reluctance_at_zero import set_element_reluctance_at_zero
from src.core.core_class.utils.for_element.get_element_volume import get_element_volume


class Element:
    def __init__(self,
                 reluctance_network=None,
                 position=None):
        
        self.position = position
        self.flat_position = None
        self.geometry = reluctance_network.geometry
        self.material_database = reluctance_network.material_database
        self.mesh = reluctance_network.mesh
        self.magnetic_potential = reluctance_network.magnetic_potential
        self.winding_current = reluctance_network.winding_current
        self.elements = reluctance_network.elements
        

        info = extract_element_info(position=position,
                                    geometry=self.geometry,
                                    mesh=self.mesh)
        
        self.material = info.material # vectorized
        self.dimension = info.dimension
        self.dimension_ratio = find_element_segment_dimension_ratio(element=self).dimension_ratio
        self.coordinate = info.coordinate

        self.segment_magnet_source = info.magnet_source
        self.magnetization_direction = info.magnetization_direction
        self.magnet_source = find_magnet_source(element=self).magnet_source # vectorized

        self.segment_winding_vector = info.winding_vector
        self.winding_normal = info.winding_normal
        self.element_winding_vector = None   # vectorized
        self.volume_error = info.volume_error

        dimension_calculated = find_element_dimension(coordinate=self.coordinate)
        self.length = dimension_calculated.length # vectorized 
        self.section_area = dimension_calculated.section_area
        self.length_ratio = dimension_calculated.length_ratio

        self.element_winding_vector = find_winding_source(element=self).element_winding_vector # 
        self.winding_source = find_winding_source(element=self).winding_source   # vectorized 
        self.magnetic_source = find_branch_magnetic_source(element=self).branch_magnetic_source  # vectorized

        self.vacuum_reluctance = find_vacuum_reluctance(length=self.length,      # vectorized
                                                        section_area=self.section_area).reluctance
        
        self.minimum_reluctance = find_minimum_reluctance(element=self).reluctance # vectorized

        self.reluctance = self.minimum_reluctance.copy()   # vectorized
        self.flux_direct = None 
        self.flux_density_direct = None
        self.flux_density_average = None
        self.relative_permeability = None
        self.d_relative_permeability_d_B = None
        self.neighbor_elements_position = get_neighbor_elements_position(element=self).neighbor_elements_position
        self.own_magnetic_potential = None

        if self.flat_position is None:
            self.flat_position = self.update_flat_position()

        self.update_element(magnetic_potential= self.magnetic_potential,
                            winding_current= self.winding_current,
                            update_for_magnetic_potential= True,
                            update_for_winding_current= True,
                            material_relaxation_factor= 1.0,
                            delta_mu_max= -1)

    def update_flat_position(self):
        self.flat_position= find_flat_position(element=self).flat_position
        return self.flat_position
    
    def neighbor_elements(self):
        return find_neighbor_elements(element=self).neighbor_elements

    def update_element(self, 
                       magnetic_potential=None, 
                       winding_current=None,
                       update_for_magnetic_potential = False,
                       update_for_winding_current = False,
                       material_relaxation_factor = 1.0,
                       delta_mu_max=-1):
        
        if update_for_winding_current:
            self.winding_current = winding_current
            self.winding_source = find_winding_source(element=self).winding_source
            self.magnetic_source = find_branch_magnetic_source(element=self).branch_magnetic_source

        if update_for_magnetic_potential:
            self.magnetic_potential = magnetic_potential
            self.flux_direct = find_flux_direct(element=self).flux_direct

            flux_density = find_flux_density(element=self)
            self.flux_density_direct = flux_density.flux_density_direct
            self.flux_density_average = flux_density.flux_density_average
            
            permeability_data = find_relative_permeability(element=self, 
                                                           material_relaxation_factor = material_relaxation_factor,
                                                           delta_mu_max= delta_mu_max)
            self.relative_permeability = permeability_data.relative_permeability
            self.d_relative_permeability_d_B = permeability_data.d_relative_permeability_d_B
            
            self.reluctance = find_reluctance_updated(element=self).reluctance
            
            self.own_magnetic_potential = find_own_magnetic_potential(element=self).own_magnetic_potential

    def set_reluctance_minimum(self):
        self.reluctance = self.minimum_reluctance.copy()

    def set_reluctance_at_zero(self):
        set_element_reluctance_at_zero(element= self)

    def get_volume(self):
        return get_element_volume(element=self)