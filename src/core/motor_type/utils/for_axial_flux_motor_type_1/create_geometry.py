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
from src.core.core_class.models.Segment import Segment
from src.core.core_class.models.Geometry import Geometry

def create_geometry(motor,
                    rotor_angle_offset = 0, # rad
                    stator_angle_offset = 0,
                    create_rotor_yoke = True,
                    create_magnet = False,
                    create_tooth = True,
                    create_stator_yoke = True):
    
    geometry = []
    
    # Truy cập các container chứa tham số nguyên bản
    stator = motor.geometry_data.stator
    rotor  = motor.geometry_data.rotor
    mmf_offset = motor.winding_data.mmf_offset

    rotor_angle_offset+= mmf_offset
    
    # --- Thành phần 1: Rotor Yoke ---
    # Sử dụng tên gốc: rotor_length thay cho rotor_yoke_axial_length
    rotor_yoke_mesh = create_tube(inner_radius=rotor.shaft_hole_diameter/2,
                                  outer_radius=rotor.rotor_lam_dia/2,
                                  height = rotor.rotor_length)
    
    rotor_yoke_template = Segment(mesh= rotor_yoke_mesh,
                                  material = "iron",
                                  magnet_source= 0.0)
                                  
    if create_rotor_yoke:
        geometry.append(rotor_yoke_template)

    # --- Thành phần 2: Nam châm vĩnh cửu ---
    pole_number = rotor.pole_number
    pole_arc = 2*pi / pole_number
    # magnet_arc thay cho magnet_arc_degree
    magnet_open_arc = pole_arc * rotor.magnet_arc / 180
    
    magnet_z_offset = rotor.rotor_length
    magnet_height = rotor.magnet_length # magnet_length thay cho magnet_axial_length
    
    magnet_coercivity = motor.material_database.magnet.coercivity
    magnet_source = magnet_coercivity * magnet_height
    
    # magnet_embed_depth thay cho magnet_embedded_depth
    magnet_outer_radius = rotor.rotor_lam_dia/2 - rotor.magnet_embed_depth
    magnet_inner_radius = magnet_outer_radius - rotor.magnet_depth

    for i in range(int(pole_number)):
        magnet_mesh = create_cylindrical_shell_segment(inner_radius=magnet_inner_radius,
                                                       outer_radius= magnet_outer_radius,
                                                       height = magnet_height,
                                                       angle_rad= magnet_open_arc,
                                                       center_angle_rad= rotor_angle_offset + i*pole_arc,
                                                       z_offset= magnet_z_offset)
        sign = 1 if i % 2 == 0 else -1

        magnet_template = Segment(mesh = magnet_mesh,
                                  material= "magnet",
                                  magnet_source= magnet_source,
                                  magnetization_direction=np.array([0,0,sign]))
                                  
        if create_magnet:
            geometry.append(magnet_template)
    
    # --- Thành phần 3: Miệng răng (Phần 1 - Bề rộng không đổi) ---
    # airgap thay cho airgap_length
    z_tooth_tip_1 = rotor.rotor_length + rotor.magnet_length + rotor.airgap
    z_tooth_tip_2 = z_tooth_tip_1 + stator.tooth_tip_depth
    
    C_in = rotor.shaft_hole_diameter * pi
    C_in_per_slot = C_in / stator.slot_number
    # slot_opening thay cho slot_opening_width
    C_in_1 = C_in_per_slot - stator.slot_opening
    angle_in_1 = 2 * np.arctan(C_in_1 / rotor.shaft_hole_diameter)

    arc_in_1 = create_arc(rotor.shaft_hole_diameter/2,
                          start_rad= stator_angle_offset - angle_in_1/2,
                          end_rad=stator_angle_offset + angle_in_1/2)
    
    C_out = stator.stator_lam_dia * pi
    C_out_per_slot = C_out / stator.slot_number
    C_out_1 = C_out_per_slot - stator.slot_opening
    angle_out_1 = 2 * np.arctan(C_out_1 / stator.stator_lam_dia)
    
    arc_out_1 = create_arc(radius= stator.stator_lam_dia/2,
                           start_rad= stator_angle_offset - angle_out_1/2,
                           end_rad= stator_angle_offset + angle_out_1/2)
    
    polygon1 = create_smart_polygon(arc1= arc_in_1, arc2= arc_out_1)
    
    mesh_1 = extrude_polygon_between_z(polygon = polygon1,
                                       z1=z_tooth_tip_1,
                                       z2=z_tooth_tip_2)
    
    for i in range(int(stator.slot_number)):
        mesh_rotated = rotate_mesh_z(mesh_1, i * 2 * pi / stator.slot_number)
        tooth_tip_rotated = Segment(mesh=mesh_rotated, material="iron")
        if create_tooth:
            geometry.append(tooth_tip_rotated)
            
    # --- Thành phần 4: Miệng răng (Phần 2 - Đoạn vát/Loft) ---
    w1 = (1/2) * (stator.slot_width - stator.slot_opening)
    h1 = w1 * np.tan(np.radians(stator.tooth_tip_angle))
    z_tooth_tip_3 = z_tooth_tip_2 + h1
    
    C_in_2 = C_in_per_slot - stator.slot_width
    angle_in_2 = 2 * np.arctan(C_in_2 / stator.stator_bore_dia)
    arc_in_2 = create_arc(radius= stator.stator_bore_dia / 2,
                          start_rad= stator_angle_offset - angle_in_2/2,
                          end_rad= stator_angle_offset + angle_in_2/2)
    
    C_out_2 = C_out_per_slot - stator.slot_width
    angle_out_2 = 2 * np.arctan(C_out_2 / stator.stator_lam_dia)
    arc_out_2 = create_arc(radius= stator.stator_lam_dia/2,
                           start_rad= stator_angle_offset - angle_out_2/2,
                           end_rad= stator_angle_offset + angle_out_2/2)
    
    polygon2 = create_smart_polygon(arc1= arc_in_2, arc2= arc_out_2)
    
    mesh2 = create_frustum_loft(poly1 = polygon1,
                                poly2= polygon2,
                                z1 = z_tooth_tip_2,
                                z2 = z_tooth_tip_3)

    for i in range(int(stator.slot_number)):
        mesh2_rotated = rotate_mesh_z(mesh = mesh2,
                                      angle_rad= i * 2 * pi / stator.slot_number)
        if create_tooth:
            geometry.append(Segment(mesh=mesh2_rotated, material="iron"))

    # --- Thành phần 5: Thân răng (Phần quấn dây) ---
    z_offset_4 = z_tooth_tip_3 + (stator.slot_depth - h1)
    mesh_3 = extrude_polygon_between_z(polygon=polygon2,
                                       z1 = z_tooth_tip_3,
                                       z2= z_offset_4)
    
    for i in range(int(stator.slot_number)):
        mesh_3_rotated = rotate_mesh_z(mesh= mesh_3,
                                       angle_rad = i * 2 * pi / stator.slot_number)
        # Truy cập winding_matrix từ container winding_data
        winding_vector = motor.winding_data.winding_matrix[i]
        if create_tooth:
            geometry.append(Segment(mesh=mesh_3_rotated,
                                    material="iron",
                                    winding_vector = winding_vector))
        
    # --- Thành phần 6: Gông Stator ---
    # stator_length thay cho stator_yoke_length
    yoke_height = stator.stator_length - stator.tooth_tip_depth - stator.slot_depth
    stator_yoke_mesh = create_tube(inner_radius=stator.stator_bore_dia / 2,
                                   outer_radius=stator.stator_lam_dia / 2,
                                   height = yoke_height,
                                   z_offset=z_offset_4)
                                   
    if create_stator_yoke:
        geometry.append(Segment(mesh = stator_yoke_mesh,
                                material="iron"))
                                
    return Geometry(geometry=geometry)