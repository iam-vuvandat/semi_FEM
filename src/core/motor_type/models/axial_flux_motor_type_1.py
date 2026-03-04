import math
from src.core.motor_type.models.Container import Container
from src.core.motor_type.models.MotorStateManager import MotorStateManager
from src.core.motor_type.models.record import Record

# Import các utility thực thi
from src.core.motor_type.utils.for_winding.generate_motor_winding_analysis import generate_motor_winding_analysis
from src.core.material.models.MaterialDataBase import MaterialDataBase
from src.core.motor_type.utils.for_axial_flux_motor_type_1.create_geometry import create_geometry
from src.core.core_class.models.ReluctanceNetwork import ReluctanceNetwork
from src.core.motor_type.utils.for_axial_flux_motor_type_1.create_adaptive_mesh import create_adaptive_mesh
from src.core.motor_type.utils.for_axial_flux_motor_type_1.rotate_rotor import rotate_rotor
from src.core.motor_type.utils.for_show.show_motor import show_motor
from src.core.solver.core.analysis_motor import analysis_motor
from src.core.motor_type.utils.for_axial_flux_motor_type_1.maxwell_stress_tensor import maxwell_stress_tensor
from src.core.motor_type.utils.for_axial_flux_motor_type_1.export_to_maxwell import export_to_maxwell
from src.core.core_class.models.Drive import Drive
from src.core.core_class.models.Mechanical import Mechanical

pi = math.pi

class AxialFluxMotorType1:
    def __init__(self):
        self.motor_type = "axial_flux_motor_type_1"
        
        # Bộ quản lý trạng thái (Nắm giữ ready_state bên trong)
        self.state_manager = MotorStateManager()

        # --- DATA CONTAINERS ---
        self.geometry_data = Container(
            stator = Container(
                slot_number          = 15,
                stator_lam_dia       = 150 * 1e-3,
                stator_bore_dia      = 50 * 1e-3,
                slot_opening         = 5 * 1e-3,
                wdg_extension_inner  = 0,
                wdg_extension_outer  = 0,
                slot_width           = 7 * 1e-3,
                slot_depth           = 15 * 1e-3,
                slot_corner_radius   = 0,
                tooth_tip_depth      = 2 * 1e-3,
                tooth_tip_angle      = 30,
                stator_length        = 25 * 1e-3
            ),
            rotor = Container(
                pole_number          = 10,
                rotor_lam_dia        = 150 * 1e-3,
                magnet_arc           = 140,
                magnet_embed_depth   = 5 * 1e-3,
                magnet_depth         = 40 * 1e-3,
                magnet_segments      = 1,
                banding_depth        = 0 * 1e-3,
                shaft_dia            = 0 * 1e-3,
                shaft_hole_diameter  = 50 * 1e-3,
                airgap               = 2 * 1e-3,
                magnet_length        = 4 * 1e-3,
                rotor_length         = 6 * 1e-3
            )
        )

        self.winding_data = Container(
            phase          = 3,
            turns          = 15,
            throw          = 1,
            parallel_path  = 1,
            winding_layer  = 2,
            mmf_offset     = 0.0,
            winding_matrix = None,
            slot_winding   = None,
            fig_layout     = None,
            fig_polar      = None,
            fig_star       = None,
            fig_mmf        = None,
            fig_wf         = None
        )
       
        self.adaptive_mesh_data = Container(
            n_r_in          = 1,
            n_r_1           = 3,
            n_r_2           = 6,
            n_r_3           = 3,
            n_r_out         = 1,
            n_theta         = 150,
            n_z_in_air      = 1,
            n_z_rotor_yoke  = 4,
            n_z_magnet      = 3,
            n_z_airgap      = 3,
            n_z_tooth_tip_1 = 1,
            n_z_tooth_tip_2 = 4,
            n_z_tooth_body  = 6,
            n_z_stator_yoke = 4,
            n_z_out_air     = 1,
            use_symmetry_factor = True,
            periodic_boundary   = True
        )

        self.material_data = Container(
            air         = "default",
            magnet_type = "NdFe30",
            iron_type   = "steel_1008"
        )

        self.calculation_data = Container(
            max_iteration          = 50,
            max_relative_residual  = 0.02,
            material_relax         = 0.35,
            n_point                = 31,
            solve_cogging          = False,
            get_geometric_error    = False,
            solve_only_1_step      = True,
            vectorized_optimization = True,
            debug                  = True
        )

        self.drive_data = Container(
            i_rms = 0.0,
            phase_advanced = 0.0
        )

        self.mechanical_data = Container(
            shaft_speed = 3000.0
        )

        self.maxwell_export_option = Container()      
        
        # --- EXECUTION ENTITIES ---
        self.geometry           = None
        self.mesh               = None
        self.reluctance_network = None
        self.drive              = None
        self.mechanical         = None
        self.material_database  = None
        self.record             = Record(motor = self)

    # --- STATE MANAGEMENT BRIDGE ---
    @property
    def ready_state(self):
        """Trả về trạng thái sẵn sàng của các thành phần máy điện."""
        return self.state_manager.ready_state

    def reload(self, 
               callback=None,
               reload_winding=False, 
               reload_material=False, 
               reload_geometry=False, 
               reload_mechanical=False, 
               reload_calculation_data=False, 
               reload_mesh=False, 
               reload_reluctance_network=False, 
               reload_drive=False):
        """Khởi tạo lại các thành phần cụ thể và thông báo qua callback."""
        return self.state_manager.reload(
            motor=self,
            callback=callback,
            reload_winding=reload_winding,
            reload_material=reload_material,
            reload_geometry=reload_geometry,
            reload_mechanical=reload_mechanical,
            reload_calculation_data=reload_calculation_data,
            reload_mesh=reload_mesh,
            reload_reluctance_network=reload_reluctance_network,
            reload_drive=reload_drive
        )

    def require(self, component_name, callback=None):
        """Đảm bảo thành phần sẵn sàng bằng cách nạp lại chuỗi phụ thuộc nếu cần."""
        return self.state_manager.require(motor=self, component_name=component_name, callback=callback)
    
    def just_changed(self, component_name):
        """Đánh dấu một thành phần đã thay đổi dữ liệu đầu vào."""
        return self.state_manager.just_changed(component_name)

    # --- PHYSICAL CREATION METHODS ---
    def create_winding(self): 
        result = generate_motor_winding_analysis(motor=self, debug=False)
        self.winding_data.mmf_offset = 0.0
        self.winding_data.winding_matrix = result.tooth_matrix
        self.winding_data.slot_matrix = result.winding_matrix
        self.winding_data.fig_layout = result.fig_layout
        self.winding_data.fig_polar  = result.fig_polar
        self.winding_data.fig_star   = result.fig_star
        self.winding_data.fig_mmf    = result.fig_mmf
        self.winding_data.fig_wf     = result.fig_wf

    def create_material_database(self): 
        self.material_database = MaterialDataBase(
            air         = self.material_data.air,
            magnet_type = self.material_data.magnet_type,
            iron_type   = self.material_data.iron_type
        )

    def create_geometry(self, **kwargs): 
        self.geometry = create_geometry(motor=self, **kwargs)

    def create_mechanical(self): 
        self.mechanical = Mechanical(motor=self)

    def create_adaptive_mesh(self): 
        self.mesh = create_adaptive_mesh(motor=self)

    def create_reluctance_network(self, callback=None): 
        self.reluctance_network = ReluctanceNetwork(
            motor    = self,
            geometry = self.geometry,
            mesh     = self.mesh,
            callback = callback
        )

    def create_drive(self): 
        self.drive = Drive(motor=self)

    # --- ANALYSIS & UTILITIES ---
    def rotate_rotor(self, n_step):
        rotate_rotor(motor=self, n_step=n_step)
    
    def analysis_motor(self, callback=None):
        return analysis_motor(motor=self, callback=callback)

    def maxwell_stress_tensor(self):
        return maxwell_stress_tensor(motor=self)

    def display(self):
        show_motor(motor=self)

    def export_to_maxwell(self, callback=None):
        return export_to_maxwell(motor=self, callback=callback)