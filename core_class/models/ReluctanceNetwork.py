from core_class.utils.for_reluctance_network.find_geometry_dimension_in_mesh import find_geometry_dimension_in_mesh
from core_class.utils.for_reluctance_network.create_elements import create_elements
from core_class.utils.for_reluctance_network.add_elements_lite import add_elements_lite
from core_class.utils.for_reluctance_network.show_reluctance_network import show_reluctance_network
from core_class.utils.for_reluctance_network.create_system_variable import create_system_variable
from core_class.utils.for_reluctance_network.create_winding_current import create_winding_current
from core_class.utils.for_reluctance_network.update_reluctance_network import update_reluctance_network
from core_class.utils.for_reluctance_network.set_minimum_reluctance import set_minimum_reluctance
from core_class.utils.for_reluctance_network.rotate_reluctance_network import rotate_reluctance_network
from core_class.utils.for_reluctance_network.set_reluctance_at_zero import set_reluctance_at_zero
from core_class.utils.for_reluctance_network.get_flux_linkage import get_flux_linkage
from solver.core.create_magnetic_potential_equation import create_magnetic_potential_equation
from solver.core.solve_magnetic_equation import solve_magnetic_equation
from solver.utils.fixed_point_iteration import fix_point_iteration
from solver.utils.advanced_solver import advanced_solver
from solver.utils.nonlinear_conjugate_gradient import nonlinear_conjugate_gradient


class ReluctanceNetwork:
    def __init__(self,
                 motor = None,
                 geometry = None,
                 mesh = None,
                 system_variable = "loop_flux",
                 loop_flux = None,
                 magnetic_potential = None,
                 winding_current = None,):
        
        self.current_position = 0.0
        self.symmetry_factor = motor.symmetry_factor
        self.material_database = motor.material_database
        self.geometry = geometry
        self.mesh = mesh
        self.system_variable = system_variable
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
    
    
    def fixed_point_iteration(self):
        return fix_point_iteration(reluctance_network = self)
    
    def advanced_solver(self, 
                    material_relax=0.5,   
                    node_damping=0.05,      
                    max_iteration=200,    
                    max_relative_residual=5e-3, 
                    debug=True):
        return advanced_solver(reluctance_network = self, 
                    material_relax=material_relax,   
                    node_damping=node_damping,      
                    max_iteration=max_iteration,    
                    max_relative_residual=max_relative_residual, 
                    debug= debug)
    
    def nonlinear_conjugate_gradient(self,
                                 max_iteration=1,
                                 max_relative_residual=5e-2,
                                 load_step=10,
                                 line_search_max=10,
                                 debug=True):
        return nonlinear_conjugate_gradient(reluctance_network = self,
                                 max_iteration= max_iteration,
                                 max_relative_residual= max_relative_residual,
                                 load_step= load_step,
                                 line_search_max= line_search_max,
                                 debug= debug)

    def solve_magnetic_equation(self,
                                method = "fixed_point_iteration",
                                max_iteration = 100,
                                max_relative_residual = 1e-4,
                                adaptive_damping_factor = (1.0,1.0),
                                load_step = 30,
                                debug = False):
        
        return solve_magnetic_equation(reluctance_network = self,
                                method = method,
                                max_iteration = max_iteration,
                                max_relative_residual = max_relative_residual,
                                adaptive_damping_factor = adaptive_damping_factor,
                                load_step = load_step,
                                debug = debug)
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
    
