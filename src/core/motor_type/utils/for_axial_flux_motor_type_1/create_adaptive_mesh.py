from src.core.motor_type.models.Container import Container
from src.core.core_class.models.CylindricalMesh import CylindricalMesh
from dataclasses import dataclass
import numpy as np
import math

pi = math.pi

def create_adaptive_mesh(motor):
    """
    Generates a 3D cylindrical mesh based on the motor's geometry and discretization parameters.
    Updated to match the refactored nested Container structure.
    """
    
    # --- 1. DATA EXTRACTION ---
    # Accessing new containers
    stator    = motor.geometry_data.stator
    rotor     = motor.geometry_data.rotor
    mesh_data = motor.adaptive_mesh_data

    # Map to long-form variable names for mesh settings
    nodes_radial_inner       = mesh_data.nodes_radial_inner
    nodes_radial_region_1    = mesh_data.nodes_radial_region_1
    nodes_radial_region_2    = mesh_data.nodes_radial_region_2
    nodes_radial_region_3    = mesh_data.nodes_radial_region_3
    nodes_radial_outer       = mesh_data.nodes_radial_outer
    nodes_tangential_theta   = mesh_data.nodes_tangential_theta
    nodes_axial_inner_air    = mesh_data.nodes_axial_inner_air
    nodes_axial_rotor_yoke   = mesh_data.nodes_axial_rotor_yoke
    nodes_axial_magnet       = mesh_data.nodes_axial_magnet
    nodes_axial_airgap       = mesh_data.nodes_axial_airgap
    nodes_axial_tooth_tip_1  = mesh_data.nodes_axial_tooth_tip_1
    nodes_axial_tooth_tip_2  = mesh_data.nodes_axial_tooth_tip_2
    nodes_axial_tooth_body   = mesh_data.nodes_axial_tooth_body
    nodes_axial_stator_yoke  = mesh_data.nodes_axial_stator_yoke
    nodes_axial_outer_air    = mesh_data.nodes_axial_outer_air
    
    use_symmetry_factor      = mesh_data.use_symmetry_factor
    periodic_boundary        = mesh_data.periodic_boundary

    # --- 2. INITIAL MESH VALIDATION ---
    # Logic remains identical: skip region 3 if magnets are not embedded
    if rotor.magnet_embedded_depth == 0:
        nodes_radial_region_3 = -1

    # Logic remains identical: skip region 1 if internal radius matches shaft hole
    if rotor.rotor_lamination_diameter / 2 - rotor.magnet_embedded_depth - rotor.magnet_depth == rotor.shaft_hole_diameter / 2:
        nodes_radial_region_1 = -1 

    # --- 3. RADIAL (R) COORDINATES GENERATION ---
    radial_segments = []
    
    # Minimum and maximum boundaries for radial mesh
    radial_min = rotor.shaft_hole_diameter/2 if stator.stator_bore_diameter > rotor.shaft_hole_diameter else stator.stator_bore_diameter/2
    radial_max = stator.stator_lamination_diameter/2 if stator.stator_lamination_diameter > rotor.rotor_lamination_diameter else rotor.rotor_lamination_diameter/2

    # Physical lengths of radial regions
    radial_length_1 = rotor.rotor_lamination_diameter / 2 - rotor.magnet_embedded_depth - rotor.magnet_depth - rotor.shaft_hole_diameter / 2
    radial_length_2 = rotor.magnet_depth
    radial_length_3 = rotor.magnet_embedded_depth

    # Segment 1: Radial Inner Air/Boundary
    if nodes_radial_inner > 0:
        radial_inner = np.linspace(radial_min * 0.9, rotor.shaft_hole_diameter / 2, nodes_radial_inner)
        radial_segments.append(radial_inner)
        radial_start_position_1 = radial_inner[-1]
    else:
        radial_start_position_1 = rotor.shaft_hole_diameter / 2

    # Segment 2: Region 1 (Internal Iron/Air)
    if nodes_radial_region_1 > 0:
        radial_region_1 = np.linspace(radial_start_position_1, radial_start_position_1 + radial_length_1, nodes_radial_region_1)
        radial_segments.append(radial_region_1[1:])
        radial_start_position_2 = radial_region_1[-1]
    else:
        radial_start_position_2 = radial_start_position_1 + radial_length_1

    # Segment 3: Region 2 (Magnet Zone)
    if nodes_radial_region_2 > 0:
        radial_region_2 = np.linspace(radial_start_position_2, radial_start_position_2 + radial_length_2, nodes_radial_region_2)
        radial_segments.append(radial_region_2[1:])
        radial_start_position_3 = radial_region_2[-1]
    else:
        radial_start_position_3 = radial_start_position_2 + radial_length_2

    # Segment 4: Region 3 (Magnet Embedding/Outer Rim)
    if nodes_radial_region_3 > 0:
        radial_region_3 = np.linspace(radial_start_position_3, radial_start_position_3 + radial_length_3, nodes_radial_region_3)
        radial_segments.append(radial_region_3[1:])
        radial_start_position_outer = radial_region_3[-1]
    else:
        radial_start_position_outer = radial_start_position_3 + radial_length_3

    # Segment 5: Radial Outer Boundary
    if nodes_radial_outer > 0:
        radial_outer = np.linspace(radial_start_position_outer, radial_start_position_outer * 1.1, nodes_radial_outer)
        radial_segments.append(radial_outer[1:])

    radial_coordinates = np.concatenate(radial_segments)

    # --- 4. TANGENTIAL (THETA) COORDINATES GENERATION ---
    if use_symmetry_factor: 
        symmetry_factor = motor.symmetry_factor
        theta_min = 0 
        theta_max = 2 * pi / symmetry_factor
        theta_coordinates = np.linspace(theta_min, theta_max, nodes_tangential_theta)
    else:
        theta_coordinates = np.linspace(0, 2 * pi, nodes_tangential_theta)

    # --- 5. AXIAL (Z) COORDINATES GENERATION ---
    axial_segments = []
    
    # Physical lengths calculation
    stator_yoke_axial_height = stator.stator_yoke_length - stator.tooth_tip_depth - stator.slot_depth
    tooth_tip_transition_width = (1/2) * (stator.slot_width - stator.slot_opening_width)
    tooth_tip_transition_height = tooth_tip_transition_width * np.tan(np.radians(stator.tooth_tip_angle))

    # Z 1. Inner Air
    if nodes_axial_inner_air > 0:
        axial_inner_air = np.linspace(-rotor.rotor_yoke_axial_length, 0, nodes_axial_inner_air)
        axial_segments.append(axial_inner_air)
        axial_start_position_1 = axial_inner_air[-1]
    else:
        axial_start_position_1 = 0

    # Z 2. Rotor Yoke
    if nodes_axial_rotor_yoke > 0:
        axial_rotor_yoke = np.linspace(axial_start_position_1, axial_start_position_1 + rotor.rotor_yoke_axial_length, nodes_axial_rotor_yoke)
        axial_segments.append(axial_rotor_yoke[1:])
        axial_start_position_2 = axial_rotor_yoke[-1]
    else:
        axial_start_position_2 = axial_start_position_1 + rotor.rotor_yoke_axial_length

    # Z 3. Magnet
    if nodes_axial_magnet > 0:
        axial_magnet = np.linspace(axial_start_position_2, axial_start_position_2 + rotor.magnet_axial_length, nodes_axial_magnet)
        axial_segments.append(axial_magnet[1:])
        axial_start_position_3 = axial_magnet[-1]
    else:
        axial_start_position_3 = axial_start_position_2 + rotor.magnet_axial_length

    # Z 4. Airgap
    if nodes_axial_airgap > 0:
        axial_airgap = np.linspace(axial_start_position_3, axial_start_position_3 + rotor.airgap_length, nodes_axial_airgap)
        axial_segments.append(axial_airgap[1:])
        axial_start_position_4 = axial_airgap[-1]
    else:
        axial_start_position_4 = axial_start_position_3 + rotor.airgap_length

    # Z 5. Tooth Tip Part 1 (Constant Width)
    if nodes_axial_tooth_tip_1 > 0:
        axial_tooth_tip_1 = np.linspace(axial_start_position_4, axial_start_position_4 + stator.tooth_tip_depth, nodes_axial_tooth_tip_1)
        if nodes_axial_tooth_tip_1 > 1:
            axial_segments.append(axial_tooth_tip_1[1:])
        axial_start_position_5 = axial_tooth_tip_1[-1]
    else:
        axial_start_position_5 = axial_start_position_4 + stator.tooth_tip_depth
        
    # Z 6. Tooth Tip Part 2 (Transition Loft)
    if nodes_axial_tooth_tip_2 > 0:
        axial_tooth_tip_2 = np.linspace(axial_start_position_5, axial_start_position_5 + tooth_tip_transition_height, nodes_axial_tooth_tip_2)
        axial_segments.append(axial_tooth_tip_2[1:])
        axial_start_position_6 = axial_tooth_tip_2[-1]
    else:
        axial_start_position_6 = axial_start_position_5 + tooth_tip_transition_height
        
    # Z 7. Tooth Body (Winding Section)
    if nodes_axial_tooth_body > 0:
        axial_tooth_body = np.linspace(axial_start_position_5, axial_start_position_5 + stator.slot_depth, nodes_axial_tooth_body)
        axial_segments.append(axial_tooth_body[1:])
        axial_start_position_7 = axial_tooth_body[-1]
    else:
        axial_start_position_7 = axial_start_position_5 + stator.slot_depth

    # Z 8. Stator Yoke
    if nodes_axial_stator_yoke > 0:
        axial_stator_yoke = np.linspace(axial_start_position_7, axial_start_position_7 + stator_yoke_axial_height, nodes_axial_stator_yoke)
        axial_segments.append(axial_stator_yoke[1:])
        axial_start_position_8 = axial_stator_yoke[-1]
    else:
        axial_start_position_8 = axial_start_position_7 + stator_yoke_axial_height

    # Z 9. Outer Air
    if nodes_axial_outer_air > 0:
        axial_outer_air = np.linspace(axial_start_position_8, axial_start_position_8 + stator_yoke_axial_height, nodes_axial_outer_air)
        axial_segments.append(axial_outer_air[1:])

    axial_coordinates = np.concatenate(axial_segments)
    
    # Returning final 3D Cylindrical Mesh object
    return CylindricalMesh(r_nodes           = radial_coordinates,
                           theta_nodes       = theta_coordinates,
                           z_nodes           = axial_coordinates,
                           periodic_boundary = periodic_boundary,
                           adaptive_mesh_data = mesh_data)