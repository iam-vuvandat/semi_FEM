import paths
from src.core.motor_type.utils.for_winding.generate_motor_winding_analysis import generate_motor_winding_analysis
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
    def __init__(self):
        
        self.motor_type = "axial_flux_motor_type_1"
        self.system_variable = "magnetic_potential"

        self.mechanical = Mechanical(shaft_speed= 3000.0,
                                     current_position= 0.0)

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

        self.material_data = Container(
            air         = "default",
            magnet_type = "NdFe30",
            iron_type   = "steel_1008"
        )

        self.material_database = MaterialDataBase(
            air         = self.material_data.air,
            magnet_type = self.material_data.magnet_type,
            iron_type   = self.material_data.iron_type
        )

        self.calculation_data = Container(
            max_iteration          = 50,
            max_relative_residual  = 0.01,
            material_relax         = 0.35,
            n_point                = 21,
            solve_cogging          = False,
            solve_only_1_step      = False,
            debug                  = True
            )
                
        self.geometry           = None
        self.mesh               = None
        self.reluctance_network = None
        self.record             = Container()

        self.reload()
        self.maxwell_export_option = Container()
        self.drive = Drive(motor = self)

    def reload(self):
        reload(motor=self)

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

    def create_geometry(self, **kwargs):
        self.geometry = create_geometry(motor=self, **kwargs)

    def create_adaptive_mesh(self):
        self.mesh = create_adaptive_mesh(motor=self)

    def create_reluctance_network(self,callback= None):
        self.reluctance_network = ReluctanceNetwork(
            motor    = self,
            geometry = self.geometry,
            mesh     = self.mesh,
            callback=callback
        )

    def rotate_rotor(self, n_step):
        rotate_rotor(motor=self, n_step=n_step)
    
    def analysis_motor(self,callback = None):
        return analysis_motor(motor = self, callback = callback)

    def maxwell_stress_tensor(self):
        return maxwell_stress_tensor(motor = self)

    def display(self):
        show_motor(motor=self)

    def export_to_maxwell(self, callback = None):
        return export_to_maxwell(motor = self, callback = callback)
    
    