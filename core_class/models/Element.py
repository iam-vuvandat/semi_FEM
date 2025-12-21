from core_class.utils.find_vacuum_reluctance import find_vacuum_reluctance
from core_class.utils.extract_element_info import extract_element_info
from core_class.utils.find_element_dimension import find_element_dimension
from core_class.utils.find_minimum_reluctance import find_minimum_reluctance
from core_class.utils.find_magnet_source import find_magnet_source
from core_class.utils.find_element_segment_dimension_ratio import find_element_segment_dimension_ratio
from core_class.utils.find_winding_source import find_winding_source
from core_class.utils.find_branch_magnetic_source import find_branch_magnetic_source
from core_class.utils.find_flux_direct import find_flux_direct
from core_class.utils.get_neighbor_elements_position import get_neighbor_elements_position
from core_class.utils.find_neighbor_elements import find_neighbor_elements
from core_class.utils.find_flux_density import find_flux_density
from core_class.utils.find_relative_permeability import find_relative_permeability
from core_class.utils.find_reluctance_updated import find_reluctance_updated
from core_class.utils.find_own_magnetic_potential import find_own_magnetic_potential
from core_class.utils.find_flat_position import find_flat_position
from core_class.utils.set_element_reluctance_at_zero import set_element_reluctance_at_zero

class Element:
    def __init__(self,
                 motor=None,
                 position=None,
                 geometry=None,
                 mesh=None,
                 magnetic_potential=None,
                 winding_current=None,
                 elements=None):
        
        self.position = position
        self.mesh = mesh
        self.material_database = motor.material_database
        self.magnetic_potential = magnetic_potential
        self.winding_current = winding_current
        self.elements = elements
        self.flat_position = find_flat_position(element=self).flat_position

        info = extract_element_info(position=position,
                                    geometry=geometry,
                                    mesh=mesh)
        
        self.material = info.material
        self.dimension = info.dimension
        self.dimension_ratio = find_element_segment_dimension_ratio(element=self).dimension_ratio
        self.coordinate = info.coordinate

        self.segment_magnet_source = info.magnet_source
        self.magnetization_direction = info.magnetization_direction
        self.magnet_source = find_magnet_source(element=self).magnet_source

        self.segment_winding_vector = info.winding_vector
        self.winding_normal = info.winding_normal
        self.element_winding_vector = None

        dimension_calculated = find_element_dimension(coordinate=self.coordinate)
        self.length = dimension_calculated.length
        self.section_area = dimension_calculated.section_area
        self.length_ratio = dimension_calculated.length_ratio

        self.element_winding_vector = find_winding_source(element=self).element_winding_vector
        self.winding_source = find_winding_source(element=self).winding_source
        self.magnetic_source = find_branch_magnetic_source(element=self).branch_magnetic_source

        self.vacuum_reluctance = find_vacuum_reluctance(length=self.length,
                                                        section_area=self.section_area).reluctance
        
        self.minimum_reluctance = find_minimum_reluctance(element=self).reluctance

        self.reluctance = self.minimum_reluctance.copy()
        self.flux_direct = None
        self.flux_density_direct = None
        self.flux_density_average = None
        self.relative_permeability = None
        self.d_relative_permeability_d_B = None
        self.neighbor_elements_position = get_neighbor_elements_position(element=self).neighbor_elements_position
        self.own_magnetic_potential = None

    def neighbor_elements(self):
        return find_neighbor_elements(element=self).neighbor_elements

    def update_element(self, magnetic_potential=None, winding_current=None):
        if winding_current is not None:
            self.winding_current = winding_current
            self.winding_source = find_winding_source(element=self).winding_source
            self.magnetic_source = find_branch_magnetic_source(element=self).branch_magnetic_source

        if magnetic_potential is not None:
            self.flux_direct = find_flux_direct(element=self).flux_direct

            flux_density = find_flux_density(element=self)
            self.flux_density_direct = flux_density.flux_density_direct
            self.flux_density_average = flux_density.flux_density_average
            
            permeability_data = find_relative_permeability(element=self)
            self.relative_permeability = permeability_data.relative_permeability
            self.d_relative_permeability_d_B = permeability_data.d_relative_permeability_d_B
            
            self.reluctance = find_reluctance_updated(element=self).reluctance
            
            self.own_magnetic_potential = find_own_magnetic_potential(element=self).own_magnetic_potential

    def set_reluctance_minimum(self):
        self.reluctance = self.minimum_reluctance.copy()

    def set_reluctance_at_zero(self):
        set_element_reluctance_at_zero(element= self)