from src.core.motor_type.models.Container import Container
from src.core.core_class.models.CylindricalMesh import CylindricalMesh
from dataclasses import dataclass
import numpy as np
import math

pi = math.pi

def create_adaptive_mesh(motor):
    """
    Generates a 3D cylindrical mesh based on the motor's geometry and discretization parameters.
    Strictly restored original variable names (e.g., n_r_in, n_z_airgap, stator_lam_dia).
    """
    
    # --- 1. TRUY XUẤT DỮ LIỆU TỪ CONTAINER NGUYÊN BẢN ---
    stator    = motor.geometry_data.stator
    rotor     = motor.geometry_data.rotor
    mesh_data = motor.adaptive_mesh_data

    # Map lại các tham số chia lưới theo tên gốc
    n_r_in          = mesh_data.n_r_in
    n_r_1           = mesh_data.n_r_1
    n_r_2           = mesh_data.n_r_2
    n_r_3           = mesh_data.n_r_3
    n_r_out         = mesh_data.n_r_out
    n_theta         = mesh_data.n_theta
    n_z_in_air      = mesh_data.n_z_in_air
    n_z_rotor_yoke  = mesh_data.n_z_rotor_yoke
    n_z_magnet      = mesh_data.n_z_magnet
    n_z_airgap      = mesh_data.n_z_airgap
    n_z_tooth_tip_1 = mesh_data.n_z_tooth_tip_1
    n_z_tooth_tip_2 = mesh_data.n_z_tooth_tip_2
    n_z_tooth_body  = mesh_data.n_z_tooth_body
    n_z_stator_yoke = mesh_data.n_z_stator_yoke
    n_z_out_air     = mesh_data.n_z_out_air
    
    use_symmetry_factor = mesh_data.use_symmetry_factor
    periodic_boundary   = mesh_data.periodic_boundary

    # --- 2. KIỂM TRA LOGIC CHIA LƯỚI ---
    # Bỏ qua vùng 3 nếu nam châm không chôn
    if rotor.magnet_embed_depth == 0:
        n_r_3 = -1

    # Bỏ qua vùng 1 nếu bán kính trong khớp với lỗ trục
    if rotor.rotor_lam_dia / 2 - rotor.magnet_embed_depth - rotor.magnet_depth == rotor.shaft_hole_diameter / 2:
        n_r_1 = -1 

    # --- 3. TẠO TỌA ĐỘ THEO PHƯƠNG XUYÊN TÂM (R) ---
    radial_segments = []
    
    # Giới hạn biên radial (Sử dụng tên biến gốc: stator_bore_dia, stator_lam_dia...)
    radial_min = rotor.shaft_hole_diameter/2 if stator.stator_bore_dia > rotor.shaft_hole_diameter else stator.stator_bore_dia/2
    radial_max = stator.stator_lam_dia/2 if stator.stator_lam_dia > rotor.rotor_lam_dia else rotor.rotor_lam_dia/2

    # Tính toán chiều dài vật lý các vùng
    radial_length_1 = rotor.rotor_lam_dia / 2 - rotor.magnet_embed_depth - rotor.magnet_depth - rotor.shaft_hole_diameter / 2
    radial_length_2 = rotor.magnet_depth
    radial_length_3 = rotor.magnet_embed_depth

    # Đoạn 1: Radial Inner Air
    if n_r_in > 0:
        radial_inner = np.linspace(radial_min * 0.9, rotor.shaft_hole_diameter / 2, n_r_in)
        radial_segments.append(radial_inner)
        radial_start_pos_1 = radial_inner[-1]
    else:
        radial_start_pos_1 = rotor.shaft_hole_diameter / 2

    # Đoạn 2: Region 1 (Internal Iron/Air)
    if n_r_1 > 0:
        radial_region_1 = np.linspace(radial_start_pos_1, radial_start_pos_1 + radial_length_1, n_r_1)
        radial_segments.append(radial_region_1[1:])
        radial_start_pos_2 = radial_region_1[-1]
    else:
        radial_start_pos_2 = radial_start_pos_1 + radial_length_1

    # Đoạn 3: Region 2 (Magnet Zone)
    if n_r_2 > 0:
        radial_region_2 = np.linspace(radial_start_pos_2, radial_start_pos_2 + radial_length_2, n_r_2)
        radial_segments.append(radial_region_2[1:])
        radial_start_pos_3 = radial_region_2[-1]
    else:
        radial_start_pos_3 = radial_start_pos_2 + radial_length_2

    # Đoạn 4: Region 3 (Magnet Embedding)
    if n_r_3 > 0:
        radial_region_3 = np.linspace(radial_start_pos_3, radial_start_pos_3 + radial_length_3, n_r_3)
        radial_segments.append(radial_region_3[1:])
        radial_start_pos_outer = radial_region_3[-1]
    else:
        radial_start_pos_outer = radial_start_pos_3 + radial_length_3

    # Đoạn 5: Radial Outer Boundary
    if n_r_out > 0:
        radial_outer = np.linspace(radial_start_pos_outer, radial_start_pos_outer * 1.1, n_r_out)
        radial_segments.append(radial_outer[1:])

    radial_coordinates = np.concatenate(radial_segments)

    # --- 4. TẠO TỌA ĐỘ THEO PHƯƠNG TIẾP TUYẾN (THETA) ---
    if use_symmetry_factor: 
        symmetry_factor = motor.symmetry_factor
        theta_max = 2 * pi / symmetry_factor
        theta_coordinates = np.linspace(0, theta_max, n_theta)
    else:
        theta_coordinates = np.linspace(0, 2 * pi, n_theta)

    # --- 5. TẠO TỌA ĐỘ THEO PHƯƠNG TRỤC (Z) ---
    axial_segments = []
    
    # Tính toán chiều dài vật lý (Sử dụng tên gốc: stator_length, slot_opening...)
    stator_yoke_height = stator.stator_length - stator.tooth_tip_depth - stator.slot_depth
    tip_transition_width = (1/2) * (stator.slot_width - stator.slot_opening)
    tip_transition_height = tip_transition_width * np.tan(np.radians(stator.tooth_tip_angle))

    # Z 1. Inner Air
    if n_z_in_air > 0:
        axial_inner_air = np.linspace(-rotor.rotor_length, 0, n_z_in_air)
        axial_segments.append(axial_inner_air)
        z_start_pos_1 = axial_inner_air[-1]
    else:
        z_start_pos_1 = 0

    # Z 2. Rotor Yoke (rotor_length)
    if n_z_rotor_yoke > 0:
        axial_rotor_yoke = np.linspace(z_start_pos_1, z_start_pos_1 + rotor.rotor_length, n_z_rotor_yoke)
        axial_segments.append(axial_rotor_yoke[1:])
        z_start_pos_2 = axial_rotor_yoke[-1]
    else:
        z_start_pos_2 = z_start_pos_1 + rotor.rotor_length

    # Z 3. Magnet (magnet_length)
    if n_z_magnet > 0:
        axial_magnet = np.linspace(z_start_pos_2, z_start_pos_2 + rotor.magnet_length, n_z_magnet)
        axial_segments.append(axial_magnet[1:])
        z_start_pos_3 = axial_magnet[-1]
    else:
        z_start_pos_3 = z_start_pos_2 + rotor.magnet_length

    # Z 4. Airgap (airgap)
    if n_z_airgap > 0:
        axial_airgap = np.linspace(z_start_pos_3, z_start_pos_3 + rotor.airgap, n_z_airgap)
        axial_segments.append(axial_airgap[1:])
        z_start_pos_4 = axial_airgap[-1]
    else:
        z_start_pos_4 = z_start_pos_3 + rotor.airgap

    # Z 5. Tooth Tip Part 1
    if n_z_tooth_tip_1 > 0:
        axial_tip_1 = np.linspace(z_start_pos_4, z_start_pos_4 + stator.tooth_tip_depth, n_z_tooth_tip_1)
        if n_z_tooth_tip_1 > 1:
            axial_segments.append(axial_tip_1[1:])
        z_start_pos_5 = axial_tip_1[-1]
    else:
        z_start_pos_5 = z_start_pos_4 + stator.tooth_tip_depth
        
    # Z 6. Tooth Tip Part 2 (Transition)
    if n_z_tooth_tip_2 > 0:
        axial_tip_2 = np.linspace(z_start_pos_5, z_start_pos_5 + tip_transition_height, n_z_tooth_tip_2)
        axial_segments.append(axial_tip_2[1:])
        z_start_pos_6 = axial_tip_2[-1]
    else:
        z_start_pos_6 = z_start_pos_5 + tip_transition_height
        
    # Z 7. Tooth Body (Winding Section)
    if n_z_tooth_body > 0:
        axial_tooth_body = np.linspace(z_start_pos_5, z_start_pos_5 + stator.slot_depth, n_z_tooth_body)
        axial_segments.append(axial_tooth_body[1:])
        z_start_pos_7 = axial_tooth_body[-1]
    else:
        z_start_pos_7 = z_start_pos_5 + stator.slot_depth

    # Z 8. Stator Yoke
    if n_z_stator_yoke > 0:
        axial_stator_yoke = np.linspace(z_start_pos_7, z_start_pos_7 + stator_yoke_height, n_z_stator_yoke)
        axial_segments.append(axial_stator_yoke[1:])
        z_start_pos_8 = axial_stator_yoke[-1]
    else:
        z_start_pos_8 = z_start_pos_7 + stator_yoke_height

    # Z 9. Outer Air
    if n_z_out_air > 0:
        axial_outer_air = np.linspace(z_start_pos_8, z_start_pos_8 + stator_yoke_height, n_z_out_air)
        axial_segments.append(axial_outer_air[1:])

    axial_coordinates = np.concatenate(axial_segments)
    
    # Trả về đối tượng lưới 3D Cylindrical Mesh
    return CylindricalMesh(r_nodes           = radial_coordinates,
                           theta_nodes       = theta_coordinates,
                           z_nodes           = axial_coordinates,
                           periodic_boundary = periodic_boundary,
                           adaptive_mesh_data = mesh_data)