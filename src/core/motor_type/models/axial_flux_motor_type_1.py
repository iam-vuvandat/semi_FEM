import paths
from src.core.motor_type.utils.for_create_geometry.find_symmetry_factor import find_symmetry_factor
from src.core.motor_type.utils.for_winding.generate_motor_winding_analysis import generate_motor_winding_analysis
from src.core.motor_type.utils.for_create_geometry.find_cogging_period import find_cogging_period
from src.core.material.models.MaterialDataBase import MaterialDataBase
from src.core.motor_type.utils.for_axial_flux_motor_type_1.create_geometry import create_geometry
from src.core.core_class.models.ReluctanceNetwork import ReluctanceNetwork
from src.core.motor_type.utils.for_axial_flux_motor_type_1.rotate_rotor import rotate_rotor
from src.core.motor_type.models.Container import Container
from src.core.motor_type.utils.for_axial_flux_motor_type_1.create_adaptive_mesh import create_adaptive_mesh
from src.core.motor_type.utils.for_show.show_motor import show_motor
from src.core.motor_type.utils.for_create_geometry.reload import reload
from src.core.solver.core.analysis_motor import analysis_motor
from src.core.motor_type.utils.for_axial_flux_motor_type_1.maxwell_stress_tensor import maxwell_stress_tensor
from src.core.motor_type.utils.for_axial_flux_motor_type_1.export_to_maxwell import export_to_maxwell

from src.core.core_class.models.Drive import Drive
from src.core.core_class.models.Mechanical import Mechanical
import math
pi = math.pi

class AxialFluxMotorType1:
    def __init__(self,
                 geometry_data      = None,
                 winding_data       = None,
                 adaptive_mesh_data = None,
                 air_material       = "default",
                 magnet_material    = "NdFe30",
                 iron_material      = "steel_1008",
                 system_variable    = "magnetic_potential"):
        
        self.motor_type = "axial_flux_motor_type_1"
        self.system_variable = system_variable
        self.mechanical = Mechanical()
        if geometry_data is None:
            self.geometry_data = self.initialize_default_geometry()
        else:
            self.geometry_data = geometry_data

        # --- Initialize Winding Container (Cải tiến: Thêm winding_matrix vào đây) ---
        if winding_data is None:
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
        else:
            self.winding_data = winding_data

        

        # --- Initialize Mesh Container ---
        if adaptive_mesh_data is None:
            self.adaptive_mesh_data = self.initialize_default_adaptive_mesh()
        else:
            self.adaptive_mesh_data = adaptive_mesh_data

        # --- External Objects & Databases ---
        self.material_database = MaterialDataBase(
            air         = air_material,
            magnet_type = magnet_material,
            iron_type   = iron_material
        )
        
        # --- Internal Simulation States ---
        self.geometry           = None
        self.mesh               = None
        self.reluctance_network = None
        self.record             = None
        self.symmetry_factor    = None
        self.cogging_period_mech = None

        self.reload()

        self.calculation_data = Container()
        self.create_calculation_data()

        # Maxwell export option
        self.maxwell_export_option = Container()
        self.drive = Drive(motor = self)

    def initialize_default_geometry(self):
        """Khởi tạo cấu trúc hình học với tên biến nguyên bản"""
        geo = Container()
        
        # Stator Parameters
        geo.stator = Container()
        geo.stator.slot_number         = 15
        geo.stator.stator_lam_dia      = 150 * 1e-3
        geo.stator.stator_bore_dia     = 50 * 1e-3
        geo.stator.slot_opening        = 5 * 1e-3
        geo.stator.wdg_extension_inner = 0
        geo.stator.wdg_extension_outer = 0
        geo.stator.slot_width          = 7 * 1e-3
        geo.stator.slot_depth          = 15 * 1e-3
        geo.stator.slot_corner_radius  = 0
        geo.stator.tooth_tip_depth     = 2 * 1e-3
        geo.stator.tooth_tip_angle     = 30
        geo.stator.stator_length       = 25 * 1e-3
        
        # Rotor Parameters
        geo.rotor = Container()
        geo.rotor.pole_number          = 10
        geo.rotor.rotor_lam_dia        = 150 * 1e-3
        geo.rotor.magnet_arc           = 140
        geo.rotor.magnet_embed_depth   = 5 * 1e-3
        geo.rotor.magnet_depth         = 40 * 1e-3
        geo.rotor.magnet_segments      = 1
        geo.rotor.banding_depth        = 0 * 1e-3
        geo.rotor.shaft_dia            = 0 * 1e-3
        geo.rotor.shaft_hole_diameter  = 50 * 1e-3
        geo.rotor.airgap               = 2 * 1e-3
        geo.rotor.magnet_length        = 4 * 1e-3
        geo.rotor.rotor_length         = 6 * 1e-3
        
        return geo

    def initialize_default_adaptive_mesh(self):
        """Khởi tạo tham số chia lưới"""
        return Container(
            n_r_in          = 1,
            n_r_1           = 2,
            n_r_2           = 4,
            n_r_3           = 2,
            n_r_out         = 1,
            n_theta         = 150,
            n_z_in_air      = 1,
            n_z_rotor_yoke  = 3,
            n_z_magnet      = 2,
            n_z_airgap      = 3,
            n_z_tooth_tip_1 = 1,
            n_z_tooth_tip_2 = 3,
            n_z_tooth_body  = 5,
            n_z_stator_yoke = 3,
            n_z_out_air     = 1,
            use_symmetry_factor = True,
            periodic_boundary   = True
        )
    
    def create_calculation_data(self):
        calculation_data = self.calculation_data
        calculation_data.max_iteration=50
        calculation_data.max_relative_residual = 0.03
        calculation_data.material_relax = 0.35
        calculation_data.solve_cogging = True
        calculation_data.n_point = 30
        calculation_data.debug = True

    # --- Utility Methods ---
    def reload(self):
        """Cập nhật trạng thái motor"""
        reload(motor=self)

    def find_symmetry_factor(self):
        """Tính toán hệ số đối xứng"""
        symmetry_data = find_symmetry_factor(motor=self)
        self.symmetry_factor = symmetry_data.symmetry_factor

    def init_winding(self):
        result = generate_motor_winding_analysis(motor= self, debug= False)
        self.winding_data.mmf_offset = 0.0
        self.winding_data.winding_matrix = result.tooth_matrix
        self.winding_data.slot_matrix = result.winding_matrix
        self.winding_data.fig_layout = result.fig_layout
        self.winding_data.fig_polar  = result.fig_polar
        self.winding_data.fig_star   = result.fig_star
        self.winding_data.fig_mmf    = result.fig_mmf
        self.winding_data.fig_wf     = result.fig_wf

    def find_cogging_period_mech(self):
        self.cogging_period_mech = find_cogging_period(slots= self.geometry_data.stator.slot_number, 
                                                       poles = self.geometry_data.rotor.pole_number).period_mech

    def create_geometry(self, **kwargs):
        """Tạo mô hình 3D CAD"""
        self.geometry = create_geometry(motor=self, **kwargs)

    def create_adaptive_mesh(self):
        """Tạo lưới tính toán"""
        self.mesh = create_adaptive_mesh(motor=self)

    def create_reluctance_network(self,callback= None):
        """Khởi tạo bộ giải mạng từ trở 3D"""
        self.reluctance_network = ReluctanceNetwork(
            motor    = self,
            geometry = self.geometry,
            mesh     = self.mesh,
            callback=callback
        )

    def rotate_rotor(self, n_step):
        """Xoay rotor cho từng bước thời gian"""
        rotate_rotor(motor=self, n_step=n_step)
    
    def reset_record(self):
        self.record = Container()

    def analysis_motor(self,callback = None):
        return analysis_motor(motor = self, callback = callback)

    def maxwell_stress_tensor(self):
        return maxwell_stress_tensor(motor = self)

    def display(self):
        show_motor(motor=self)

    def export_to_maxwell(self):
        return export_to_maxwell(motor = self)
    
    