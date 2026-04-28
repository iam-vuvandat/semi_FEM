import trimesh
import numpy as np
import math 
pi = math.pi

from src.core.motor_type.utils.for_create_geometry.create_tube import create_tube
from src.core.motor_type.utils.for_create_geometry.create_cylindrical_shell_segment import create_cylindrical_shell_segment
from src.core.motor_type.utils.for_create_geometry.create_smart_poligon import create_smart_polygon
from src.core.motor_type.utils.for_create_geometry.extrude_polygon_between_z import extrude_polygon_between_z
from src.core.motor_type.utils.for_create_geometry.create_arc import create_arc
from src.core.motor_type.utils.for_create_geometry.rotate_mesh_z import rotate_mesh_z
from src.core.motor_type.utils.for_create_geometry.create_frustum_loft import create_frustum_loft
from src.core.motor_type.utils.for_create_geometry.create_symmetry_sector import create_symmetry_sector
from src.core.motor_type.utils.for_create_geometry.get_geometry_in_sector import get_geometry_in_sector

from src.core.core_class.models.Segment import Segment
from src.core.core_class.models.Geometry import Geometry

def create_geometry(motor,
                    rotor_angle_offset = 0, # rad
                    stator_angle_offset = 0,
                    create_rotor_yoke = True,
                    create_magnet = True,
                    create_tooth = True,
                    create_stator_yoke = True):

    motor.require('mechanical')
    geometry = []
    
    stator = motor.geometry_data.stator
    rotor  = motor.geometry_data.rotor

    # create symmetry sector
    use_symmetry_factor = motor.adaptive_mesh_data.use_symmetry_factor
    motor_height = (stator.slot_depth + stator.stator_length + rotor.rotor_length ) * 2
    symmetry_factor = motor.mechanical.symmetry_factor
    motor_radius = stator.stator_lam_dia + rotor.rotor_lam_dia 

    # Luôn tạo khuôn cắt, nếu không dùng symmetry thì factor = 1 (360 độ)
    current_sym_factor = symmetry_factor if use_symmetry_factor else 1
    symmetry_sector = create_symmetry_sector(height=motor_height, symmetry_factor=current_sym_factor, radius=motor_radius)

    mmf_offset = motor.winding_data.mmf_offset
    rotor_angle_offset += mmf_offset 
    
    synchronize_with_rmxprt = motor.geometry_data.geometry_option.synchronize_with_rmxprt
    if synchronize_with_rmxprt:
        offset_rotor_for_rmxprt = (2* pi / (rotor.pole_number)) / 2
        offset_stator_for_rmxprt = (2 * pi) / (stator.slot_number)
        stator_angle_offset += offset_stator_for_rmxprt
        rotor_angle_offset += offset_rotor_for_rmxprt
        motor.mechanical.current_position += offset_rotor_for_rmxprt - offset_stator_for_rmxprt
        motor.geometry_data.geometry_option.rotor_mechanical_synchronized = offset_rotor_for_rmxprt - offset_stator_for_rmxprt

    # --- Thành phần 1: Rotor Yoke ---
    if create_rotor_yoke:
        rotor_yoke_mesh = create_tube(inner_radius=rotor.shaft_hole_diameter/2,
                                      outer_radius=rotor.rotor_lam_dia/2,
                                      height=rotor.rotor_length)
        mesh_cut, state = get_geometry_in_sector(target_mesh=rotor_yoke_mesh, sector_mesh=symmetry_sector)
        if state:
            geometry.append(Segment(mesh=mesh_cut, material="iron", magnet_source=0.0))

    # --- Thành phần 2: Nam châm vĩnh cửu ---
    if create_magnet:
        pole_number = rotor.pole_number
        pole_arc = 2*pi / pole_number
        magnet_open_arc = pole_arc * rotor.magnet_arc / 180
        magnet_z_offset = rotor.rotor_length
        magnet_height = rotor.magnet_length
        magnet_coercivity = motor.material_database.magnet.coercivity
        magnet_source = magnet_coercivity * magnet_height
        magnet_outer_radius = rotor.rotor_lam_dia/2 - rotor.magnet_embed_depth
        magnet_inner_radius = magnet_outer_radius - rotor.magnet_depth

        for i in range(int(pole_number)):
            magnet_mesh = create_cylindrical_shell_segment(inner_radius=magnet_inner_radius,
                                                           outer_radius=magnet_outer_radius,
                                                           height=magnet_height,
                                                           angle_rad=magnet_open_arc,
                                                           center_angle_rad=rotor_angle_offset + i*pole_arc,
                                                           z_offset=magnet_z_offset)
            mesh_cut, state = get_geometry_in_sector(target_mesh=magnet_mesh, sector_mesh=symmetry_sector)
            if state:
                sign = 1 if i % 2 == 0 else -1
                geometry.append(Segment(mesh=mesh_cut, material="magnet", magnet_source=magnet_source,
                                        magnetization_direction=np.array([0,0,sign])))
    
    # --- Thành phần 3, 4, 5 (Teeth) ---
    if create_tooth:
        # Pre-calculations cho Tooth
        z_tooth_tip_1 = rotor.rotor_length + rotor.magnet_length + rotor.airgap
        z_tooth_tip_2 = z_tooth_tip_1 + stator.tooth_tip_depth
        C_in_per_slot = (rotor.shaft_hole_diameter * pi) / stator.slot_number
        angle_in_1 = 2 * np.arctan((C_in_per_slot - stator.slot_opening) / rotor.shaft_hole_diameter)
        arc_in_1 = create_arc(rotor.shaft_hole_diameter/2, stator_angle_offset - angle_in_1/2, stator_angle_offset + angle_in_1/2)
        angle_out_1 = 2 * np.arctan(((stator.stator_lam_dia * pi / stator.slot_number) - stator.slot_opening) / stator.stator_lam_dia)
        arc_out_1 = create_arc(stator.stator_lam_dia/2, stator_angle_offset - angle_out_1/2, stator_angle_offset + angle_out_1/2)
        polygon1 = create_smart_polygon(arc1=arc_in_1, arc2=arc_out_1)
        
        # Loft/Body parts
        w1 = (1/2) * (stator.slot_width - stator.slot_opening)
        h1 = w1 * np.tan(np.radians(stator.tooth_tip_angle))
        z_tooth_tip_3 = z_tooth_tip_2 + h1
        angle_in_2 = 2 * np.arctan(((C_in_per_slot * stator.slot_number / stator.slot_number) - stator.slot_width) / stator.stator_bore_dia)
        arc_in_2 = create_arc(stator.stator_bore_dia/2, stator_angle_offset - angle_in_2/2, stator_angle_offset + angle_in_2/2)
        angle_out_2 = 2 * np.arctan(((stator.stator_lam_dia * pi / stator.slot_number) - stator.slot_width) / stator.stator_lam_dia)
        arc_out_2 = create_arc(stator.stator_lam_dia/2, stator_angle_offset - angle_out_2/2, stator_angle_offset + angle_out_2/2)
        polygon2 = create_smart_polygon(arc1=arc_in_2, arc2=arc_out_2)
        z_offset_4 = z_tooth_tip_3 + (stator.slot_depth - h1)

        # Base meshes
        mesh_tip_base = extrude_polygon_between_z(polygon=polygon1, z1=z_tooth_tip_1, z2=z_tooth_tip_2)
        mesh_loft_base = create_frustum_loft(poly1=polygon1, poly2=polygon2, z1=z_tooth_tip_2, z2=z_tooth_tip_3)
        mesh_body_base = extrude_polygon_between_z(polygon=polygon2, z1=z_tooth_tip_3, z2=z_offset_4)

        for i in range(int(stator.slot_number)):
            rot_angle = i * 2 * pi / stator.slot_number
            # Xử lý Tip 1
            t1_rot = rotate_mesh_z(mesh_tip_base, rot_angle)
            m1_cut, s1 = get_geometry_in_sector(t1_rot, symmetry_sector)
            if s1: geometry.append(Segment(mesh=m1_cut, material="iron"))
            # Xử lý Loft
            t2_rot = rotate_mesh_z(mesh_loft_base, rot_angle)
            m2_cut, s2 = get_geometry_in_sector(t2_rot, symmetry_sector)
            if s2: geometry.append(Segment(mesh=m2_cut, material="iron"))
            # Xử lý Body
            t3_rot = rotate_mesh_z(mesh_body_base, rot_angle)
            m3_cut, s3 = get_geometry_in_sector(t3_rot, symmetry_sector)
            if s3: geometry.append(Segment(mesh=m3_cut, material="iron", winding_vector=motor.winding_data.winding_matrix[i]))

    # --- Thành phần 6: Gông Stator ---
    if create_stator_yoke:
        yoke_height = stator.stator_length - stator.tooth_tip_depth - stator.slot_depth
        z_yoke = z_tooth_tip_3 + (stator.slot_depth - h1) # z_offset_4
        stator_yoke_mesh = create_tube(inner_radius=stator.stator_bore_dia/2, 
                                       outer_radius=stator.stator_lam_dia/2, 
                                       height=yoke_height, z_offset=z_yoke)
        mesh_cut, state = get_geometry_in_sector(target_mesh=stator_yoke_mesh, sector_mesh=symmetry_sector)
        if state:
            geometry.append(Segment(mesh=mesh_cut, material="iron"))
                                
    return Geometry(geometry=geometry)