# Core Class Utils

from src.core.core_class.utils.for_reluctance_network.find_geometry_dimension_in_mesh import find_geometry_dimension_in_mesh
from src.core.core_class.utils.for_reluctance_network.create_elements import create_elements
from src.core.core_class.utils.for_reluctance_network.add_elements_lite import add_elements_lite
from src.core.core_class.utils.for_reluctance_network.show_reluctance_network import show_reluctance_network
from src.core.core_class.utils.for_reluctance_network.create_system_variable import create_system_variable
from src.core.core_class.utils.for_reluctance_network.create_winding_current import create_winding_current
from src.core.core_class.utils.for_reluctance_network.update_reluctance_network import update_reluctance_network
from src.core.core_class.utils.for_reluctance_network.set_minimum_reluctance import set_minimum_reluctance
from src.core.core_class.utils.for_reluctance_network.rotate_reluctance_network import rotate_reluctance_network
from src.core.core_class.utils.for_reluctance_network.set_reluctance_at_zero import set_reluctance_at_zero
from src.core.core_class.utils.for_reluctance_network.get_flux_linkage import get_flux_linkage
from src.core.core_class.utils.for_reluctance_network.access_elements import access_elements
from src.core.core_class.utils.for_reluctance_network.display_reluctance_network import display_reluctance_network
from src.core.core_class.utils.for_reluctance_network.get_geometric_error import get_geometric_error
from src.core.core_class.utils.for_reluctance_network.display_elements import display_elements
from src.core.core_class.utils.for_reluctance_network.create_vectorized_elements import init_vectorized_elements
from src.core.core_class.utils.for_reluctance_network.update_elements_from_vectorized import update_elements_from_vectorized
from src.core.core_class.utils.for_reluctance_network.get_airgap_flux_density import get_airgap_flux_density

# Solver Core
from src.core.solver.model.Solver import Solver
from src.core.solver.core.create_magnetic_potential_equation import create_magnetic_potential_equation
from src.core.solver.core.solve import solve

class ReluctanceNetwork:
    def __init__(self,
                 motor = None,
                 geometry = None,
                 mesh = None,
                 magnetic_potential = None,
                 winding_current = None,
                 callback = None):
        
        self.geometry_data = motor.geometry_data
        self.mechanical = motor.mechanical
        self.symmetry_factor = motor.mechanical.symmetry_factor
        self.calculation_data = motor.calculation_data
        self.vectorized_optimization = self.calculation_data.general_options.vectorized_optimization
        self.material_database = motor.material_database
        self.geometry = geometry
        self.geometric_error = 0.0
        self.mesh = mesh
        self.system_variable = "magnetic_potential"
        self.magnetic_potential = magnetic_potential
        self.winding_current = winding_current
        self.vectorized_elements = None
        find_geometry_dimension_in_mesh(geometry= geometry,
                                        mesh= mesh)
        
        self.winding_current = create_winding_current(reluctance_network=self)

        system_variable_data = create_system_variable(reluctance_network=self)
        self.magnetic_potential = system_variable_data.magnetic_potential

        self.elements = None
        self.elements = self.create_elements(callback = callback)

        self.vectorized_elements = init_vectorized_elements(reluctance_network= self)
        
        
        self.list_elements_lite = None

        self.solver = Solver(reluctance_network= self)

    def create_elements(self,callback = None):
        return create_elements(reluctance_network= self, callback = callback)
    
    def add_elements_lite(self):
        add_elements_lite(reluctance_network = self)
    
    def access_elements(self,position):
        return access_elements(reluctance_network=self,
                               position=position)

    def update_reluctance_network(self,
                                  magnetic_potential = None,
                                  winding_current = None,
                                  update_for_magnetic_potential = False,
                                  update_for_winding_current = False,
                                  material_relaxation_factor = 1.0,
                                  delta_mu_max=-1):
        
        update_reluctance_network(reluctance_network=self,
                                  magnetic_potential = magnetic_potential,
                                  winding_current = winding_current,
                                  update_for_magnetic_potential= update_for_magnetic_potential,
                                  update_for_winding_current = update_for_winding_current,
                                  material_relaxation_factor = material_relaxation_factor,
                                  delta_mu_max= delta_mu_max)

    def set_minimum_reluctance(self):
        set_minimum_reluctance(reluctance_network=self)

    def set_reluctance_at_zero(self):
        set_reluctance_at_zero(reluctance_network = self)

    def create_magnetic_potential_equation(self,
                                           load_factor = 1.0,
                                           debug = False):
        return create_magnetic_potential_equation(reluctance_network= self,
                                                  load_factor= load_factor,
                                                  debug = debug)
    
    def rotate(self,
               z_indices = [0,1,2],
               n_step = 1):
        rotate_reluctance_network(reluctance_network = self,
                              z_indices = z_indices,
                              n_step = n_step)

    def get_flux_linkage(self):
        return get_flux_linkage(reluctance_network=self)
    

    def get_geometric_error(self):
        self.geometric_error = get_geometric_error(reluctance_network=self)
        
    def display(self,plotter = None):
        return display_reluctance_network(reluctance_network=self, plotter = plotter)
    
    def show_elements(self):
        return display_elements(reluctance_network=self)
    
    def refresh_elements(self):
        update_elements_from_vectorized(reluctance_network= self)
    
    def export_airgap_flux_density(self,path_sweep = [0,-1,0]):
        return get_airgap_flux_density(reluctance_network= self, path_sweep= path_sweep)