from src.core.motor_type.utils.for_axial_flux_motor_type_1.find_symmetry_factor import find_symmetry_factor
from src.core.motor_type.utils.for_axial_flux_motor_type_1.find_winding_matrix import find_winding_matrix
from src.core.material.models.MaterialDataBase import MaterialDataBase
from src.core.motor_type.utils.for_axial_flux_motor_type_1.create_geometry import create_geometry
from src.core.core_class.models.ReluctanceNetwork import ReluctanceNetwork
from src.core.motor_type.utils.for_axial_flux_motor_type_1.rotate_rotor import rotate_rotor
from src.core.motor_type.models.Container import Container
from src.core.motor_type.utils.for_axial_flux_motor_type_1.create_adaptive_mesh import create_adaptive_mesh
from src.core.motor_type.utils.for_show.show_motor import show_motor
from src.core.motor_type.utils.for_create_geometry.reload import reload

import pyvista as pv
import math
pi = math.pi

class AxialFluxMotorType1:
    def __init__(self,
                 geometry_data      = None,
                 winding_data       = None,
                 adaptive_mesh_data = None,
                 air_material       = "default",
                 magnet_material    = "N30UH",
                 iron_material      = "M350-50A",
                 shaft_speed        = 3000,
                 system_variable    = "magnetic_potential"):
        
        # --- Basic Identification ---
        self.motor_type = "axial_flux_motor_type_1"
        self.shaft_speed = shaft_speed
        self.system_variable = system_variable

        # --- Initialize Geometry Container ---
        if geometry_data is None:
            self.geometry_data = self.initialize_default_geometry()
        else:
            self.geometry_data = geometry_data

        # --- Initialize Winding Container ---
        if winding_data is None:
            self.winding_data = Container(
                phase_number   = 3,
                turns_number   = 50,
                coil_throw     = 1,
                parallel_path  = 1,
                winding_layer  = 2,
                winding_type   = "concentrated"
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
        self.record             = Container()
        self.symmetry_factor    = None
        self.winding_matrix     = None

        # --- Immediate Calculations ---
        self.find_symmetry_factor()
        self.find_winding_matrix()

    def initialize_default_geometry(self):
        """Creates a default geometry structure with Stator and Rotor containers"""
        geo = Container()
        
        # Stator Parameters
        geo.stator = Container()
        geo.stator.slot_number                 = 15
        geo.stator.stator_lamination_diameter  = 150 * 1e-3
        geo.stator.stator_bore_diameter        = 50 * 1e-3
        geo.stator.slot_opening_width          = 5 * 1e-3
        geo.stator.winding_extension_inner     = 0
        geo.stator.winding_extension_outer     = 0
        geo.stator.slot_width                  = 7 * 1e-3
        geo.stator.slot_depth                  = 15 * 1e-3
        geo.stator.slot_corner_radius          = 0
        geo.stator.tooth_tip_depth             = 2 * 1e-3
        geo.stator.tooth_tip_angle             = 30
        geo.stator.stator_yoke_length          = 25 * 1e-3
        
        # Rotor Parameters
        geo.rotor = Container()
        geo.rotor.pole_number                  = 10
        geo.rotor.rotor_lamination_diameter    = 150 * 1e-3
        geo.rotor.magnet_arc_degree            = 140
        geo.rotor.magnet_embedded_depth        = 5 * 1e-3
        geo.rotor.magnet_depth                 = 40 * 1e-3
        geo.rotor.magnet_segments              = 1
        geo.rotor.banding_depth                = 0 * 1e-3
        geo.rotor.shaft_diameter               = 0 * 1e-3
        geo.rotor.shaft_hole_diameter          = 50 * 1e-3
        geo.rotor.airgap_length                = 2 * 1e-3
        geo.rotor.magnet_axial_length          = 4 * 1e-3
        geo.rotor.rotor_yoke_axial_length      = 6 * 1e-3
        
        return geo

    def initialize_default_adaptive_mesh(self):
        """Initializes default discretization parameters for the 3D solver"""
        return Container(
            nodes_radial_inner      = 2,
            nodes_radial_region_1   = 3,
            nodes_radial_region_2   = 6,
            nodes_radial_region_3   = 3,
            nodes_radial_outer      = 2,
            nodes_tangential_theta  = 70,
            nodes_axial_inner_air   = 2,
            nodes_axial_rotor_yoke  = 3,
            nodes_axial_magnet      = 3,
            nodes_axial_airgap      = 3,
            nodes_axial_tooth_tip_1 = 3,
            nodes_axial_tooth_tip_2 = 3,
            nodes_axial_tooth_body  = 6,
            nodes_axial_stator_yoke = 3,
            nodes_axial_outer_air   = 2,
            use_symmetry_factor     = True,
            periodic_boundary       = True
        )

    # --- Utility Methods ---
    def reload(self):
        """Reloads the motor state by clearing geometry and mesh"""
        reload(motor=self)

    def find_symmetry_factor(self):
        """Calculates the machine symmetry factor based on geometry"""
        symmetry_data = find_symmetry_factor(motor=self)
        self.symmetry_factor = symmetry_data.symmetry_factor

    def find_winding_matrix(self):
        """Generates the winding layout matrix"""
        winding_data = find_winding_matrix(motor=self)
        self.winding_matrix = winding_data.winding_matrix

    def create_geometry(self, **kwargs):
        """Constructs the 3D CAD representation of the motor"""
        self.geometry = create_geometry(motor=self, **kwargs)

    def create_adaptive_mesh(self):
        """Generates the 3D computational mesh"""
        self.mesh = create_adaptive_mesh(motor=self)

    def create_reluctance_network(self):
        """Initializes the 3D General Reluctance Network solver"""
        self.reluctance_network = ReluctanceNetwork(
            motor    = self,
            geometry = self.geometry,
            mesh     = self.mesh
        )

    def rotate_rotor(self, n_step):
        """Updates rotor position and boundary conditions for a time step"""
        rotate_rotor(motor=self, n_step=n_step)

    def display(self):
        """Wrapper for external motor display utility"""
        show_motor(motor=self)