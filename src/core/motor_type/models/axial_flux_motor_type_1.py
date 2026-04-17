import math
import numpy as np
from types import SimpleNamespace
from src.core.motor_type.models.MotorStateManager import MotorStateManager
from src.core.core_class.models.Drive import Drive
from src.core.core_class.models.Mechanical import Mechanical
from src.core.material.models.MaterialDataBase import MaterialDataBase
from src.core.core_class.models.ReluctanceNetwork import ReluctanceNetwork
from src.core.core_class.models.DataProcessor import DataProcessor

from src.core.motor_type.utils.for_winding.generate_motor_winding_analysis import generate_motor_winding_analysis
from src.core.motor_type.utils.for_axial_flux_motor_type_1.create_geometry import create_geometry
from src.core.motor_type.utils.for_axial_flux_motor_type_1.rotate_rotor import rotate_rotor
from src.core.motor_type.utils.for_axial_flux_motor_type_1.create_adaptive_mesh import create_adaptive_mesh
from src.core.motor_type.utils.for_show.show_motor import show_motor
from src.core.solver.core.analysis_motor import analysis_motor
from src.core.motor_type.utils.for_axial_flux_motor_type_1.maxwell_stress_tensor import maxwell_stress_tensor
from src.core.motor_type.utils.for_axial_flux_motor_type_1.export_to_maxwell import export_to_maxwell
from src.core.motor_type.utils.for_export_maxwell.update_maxwell_settings import update_maxwell_settings

from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.export_to_rmxprt import export_to_rmxprt

pi = math.pi

class AxialFluxMotorType1:
    def __init__(self):
        self.motor_state_manager = MotorStateManager()
        self.data_processor = DataProcessor(motor=self)

        self.material_database = None
        self.winding_data = None
        self.mechanical = None
        self.geometry = None
        self.calculation_data = None
        self.mesh = None
        self.reluctance_network = None
        self.drive = None
        self.record = SimpleNamespace()
    
        self.material_data = SimpleNamespace(
            air         = "default",
            magnet_type = "NdFe30",
            iron_type   = "steel_1008"
        )

        self.winding_data = SimpleNamespace(
            phase          = 3,
            turns          = 20,
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

        self.mechanical_data = SimpleNamespace(
            shaft_speed = 3000
        )

        self.geometry_data = SimpleNamespace(
            stator = SimpleNamespace(
                slot_number          = 15,
                stator_lam_dia       = 150 * 1e-3,
                stator_bore_dia      = 70 * 1e-3,
                slot_opening         = 2 * 1e-3,
                wdg_extension_inner  = 0,
                wdg_extension_outer  = 0,
                slot_width           = 7 * 1e-3,
                slot_depth           = 15 * 1e-3,
                slot_corner_radius   = 0,
                tooth_tip_depth      = 2 * 1e-3,
                tooth_tip_angle      = 30,
                stator_length        = 25 * 1e-3
            ),
            rotor = SimpleNamespace(
                pole_number          = 10,
                rotor_lam_dia        = 150 * 1e-3,
                magnet_arc           = 160,
                magnet_embed_depth   = 5 * 1e-3,
                magnet_depth         = 30 * 1e-3,
                magnet_segments      = 1,
                banding_depth        = 0 * 1e-3,
                shaft_dia            = 0 * 1e-3,
                shaft_hole_diameter  = 70 * 1e-3,
                airgap               = 1.5 * 1e-3,
                magnet_length        = 3 * 1e-3,
                rotor_length         = 6 * 1e-3
            ),
            geometry_option = SimpleNamespace(
                synchronize_with_rmxprt = True,
                rotor_mechanical_synchronized = 0.0
            )
        )

        self.calculation_data = SimpleNamespace(
            convergence_settings = SimpleNamespace(
                max_iteration          = 50,
                max_relative_residual  = 1 * 1e-2,
                material_relax         = 0.35,
                damping_factor         = 1.0,
                relaxation_history     = None,
                relaxation_decay = 0.5
            ),
            general_options = SimpleNamespace(
                n_point                = 20,
                solve_cogging          = True,
                solve_smooth_torque    = False,
                solve_only_1_step      = False,
                vectorized_optimization = True,
                get_geometric_error    = False,
                debug                  = True
            ),  
            export_inductance_options = SimpleNamespace(
                export_inductance = False,
                current_min       = 1.0,
                current_max       = 15.0,
                current_resolution = 10
            )  
        )

        self.adaptive_mesh_data = SimpleNamespace(
            n_r_in          = 2,
            n_r_1           = 4,
            n_r_2           = 7,
            n_r_3           = 4,
            n_r_out         = 2,
            n_theta         = 150,
            n_z_in_air      = 2,
            n_z_rotor_yoke  = 6,
            n_z_magnet      = 4,
            n_z_airgap      = 5,
            n_z_tooth_tip_1 = 3,
            n_z_tooth_tip_2 = 6,
            n_z_tooth_body  = 8,
            n_z_stator_yoke = 6,
            n_z_out_air     = 2,
            use_symmetry_factor = True,
            periodic_boundary   = True
        )

        self.drive_data = SimpleNamespace(
            i_rms = 10.0,
            phase_advanced = 0.0
        )

        self.maxwell_export_option = SimpleNamespace(
            ansys_electronic_version = "2025.2",
            use_default_option = True,
            custom_option = SimpleNamespace(
                mesh_setting = SimpleNamespace(
                    cylindrical_gap_1= SimpleNamespace(
                        clone_mesh = False,
                        mapping_angle = -1,
                        moving_side = 1,
                        static_side = 1
                    ),

                    band_mapping_angle = pi / 180,
                    maximum_element_length = 20 * 1e-3, # unit: m
                    airgap_element_layer = 6,
                    moving_side_layers = 1,
                    static_side_layers = 1,
                    length_band_element_length = -1,
                    length_coil_element_length = -1,
                    length_mag_element_length = -1,
                    length_main_element_length = -1,
                    length_region_element_length = -1
                ),
                motion_setting = SimpleNamespace(
                    shaft_speed = 3000
                ),
            ),
            current_function = None,
            current_function_for_rmxprt_export = None,
            solver_option = SimpleNamespace(
                alternetive_first_point = True,
                solve_immediately = True,
                solve_only_1_step = False
            ),
        )

    def create_material_database(self): 
        self.material_database = MaterialDataBase(
            air         = self.material_data.air,
            magnet_type = self.material_data.magnet_type,
            iron_type   = self.material_data.iron_type
        )

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

    def create_mechanical(self):
        self.mechanical = Mechanical(motor= self)
    
    def create_geometry(self, **kwargs): 
        self.geometry = create_geometry(motor=self, **kwargs)

    def create_calculation_data(self):
        pass

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
    
    def export_to_rmxprt(self):
        return export_to_rmxprt(motor = self )

    def just_changed(self, component_name):
        return self.motor_state_manager.just_changed(component_name)

    def require(self, component_name, callback=None):
        return self.motor_state_manager.require(motor=self, component_name=component_name, callback=callback)

    def reload(self, callback=None, **kwargs):
        return self.motor_state_manager.reload(motor=self, callback=callback, **kwargs)
    
    def update_maxwell_setting(self):
        update_maxwell_settings(motor=self)

        