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

# Solver Core
from src.core.solver.core.create_magnetic_potential_equation import create_magnetic_potential_equation
from src.core.solver.core.create_loop_flux_equation import create_loop_flux_equation
from src.core.solver.core.solve import solve


class ReluctanceNetwork:
    def __init__(self,
                 motor = None,
                 geometry = None,
                 mesh = None,
                 loop_flux = None,
                 magnetic_potential = None,
                 winding_current = None,):
        
        self.current_position = 0.0
        self.symmetry_factor = motor.symmetry_factor
        self.material_database = motor.material_database
        self.geometry = geometry
        self.mesh = mesh
        self.system_variable = motor.system_variable
        self.loop_flux = loop_flux
        self.magnetic_potential = magnetic_potential
        self.winding_current = winding_current
        find_geometry_dimension_in_mesh(geometry= geometry,
                                        mesh= mesh)
        
        self.winding_current = create_winding_current(reluctance_network=self)

        system_variable_data = create_system_variable(reluctance_network=self)
        self.magnetic_potential = system_variable_data.magnetic_potential
        self.loop_flux = system_variable_data.loop_flux

        self.elements = None
        self.elements = create_elements(self)
        self.list_elements_lite = None

    def add_elements_lite(self):
        add_elements_lite(reluctance_network = self)
    
    def access_elements(self,position):
        return access_elements(reluctance_network=self,
                               position=position)

    def update_reluctance_network(self,
                                  loop_flux = None,
                                  magnetic_potential = None,
                                  winding_current = None,
                                  material_relaxation_factor = 1.0,
                                  delta_mu_max=-1):
        
        update_reluctance_network(reluctance_network=self,
                                  loop_flux = loop_flux,
                                  magnetic_potential = magnetic_potential,
                                  winding_current = winding_current,
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
    
    def create_loop_flux_equation(self,
                                  load_factor = 1.0,
                                  create_jacobian = False,
                                  debug = True):
        return create_loop_flux_equation(reluctance_network = self,
                                         load_factor = load_factor,
                                         create_jacobian = create_jacobian,
                                         debug = debug)
    
    def solve(self,
              method = "fixed_point_iteration",
              max_iteration=50,
              material_relax=0.5, 
              damping_factor = 0.05,   
              debug = False):
        
        solve(reluctance_network= self,
              method= method,
              max_iteration= max_iteration,
              material_relax= material_relax,
              damping_factor= damping_factor,
              debug= debug)



    def rotate(self,
               z_indices = [0,1,2],
               n_step = 1):
        rotate_reluctance_network(reluctance_network = self,
                              z_indices = z_indices,
                              n_step = n_step)

    def get_flux_linkage(self):
        return get_flux_linkage(reluctance_network=self)

    def show(self,
             use_symmetry_factor = True):
        show_reluctance_network(reluctance_network=self,
                                use_symmetry_factor = use_symmetry_factor)
    
