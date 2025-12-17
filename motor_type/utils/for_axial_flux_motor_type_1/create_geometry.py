import trimesh
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
import math 
pi = math.pi

from motor_type.utils.for_create_geometry.create_cylinder import create_cylinder
from motor_type.utils.for_create_geometry.create_tube import create_tube
from motor_type.utils.for_create_geometry.create_cylindrical_shell_segment import create_cylindrical_shell_segment
from motor_type.utils.for_create_geometry.create_smart_poligon import create_smart_polygon
from motor_type.utils.for_create_geometry.extrude_polygon_between_z import extrude_polygon_between_z
from motor_type.utils.for_create_geometry.create_arc import create_arc
from motor_type.utils.for_create_geometry.rotate_mesh_z import rotate_mesh_z
from motor_type.utils.for_create_geometry.create_frustum_loft import create_frustum_loft
from core_class.models.Segment import Segment
from core_class.models.Geometry import Geometry



def create_geometry(motor,
                    rotor_angle_offset = 0, #rad
                    stator_angle_offset = 0,
                    create_rotor_yoke = True,
                    create_magnet = True,
                    create_tooth = True,
                    create_stator_yoke = True): #rad
    
    geometry = []
    
    # create_rotor_yoke
    rotor_yoke_mesh = create_tube(inner_radius=motor.shaft_hole_diameter/2,
                                  outer_radius=motor.rotor_lam_dia/2,
                                  height = motor.rotor_length,
                                )
    rotor_yoke_template = Segment(mesh= rotor_yoke_mesh,
                                  material = "iron",
                                  magnet_source= 0.0,
                                  )
    if create_rotor_yoke == True:
        geometry.append(rotor_yoke_template)

    #create_magnet
    pole_number = motor.pole_number
    pole_arc = 2*pi / pole_number
    magnet_open_arc = pole_arc * motor.magnet_arc /180
    magnet_z_offset = motor.rotor_length
    magnet_height = motor.magnet_length
    magnet_coercivity = motor.material_database.magnet.coercivity
    magnet_source = magnet_coercivity * magnet_height
    magnet_outer_radius = motor.rotor_lam_dia/2 - motor.magnet_embed_depth
    magnet_inner_radius = magnet_outer_radius - motor.magnet_depth

    for i in range(int(pole_number)):
        magnet_mesh = create_cylindrical_shell_segment(inner_radius=magnet_inner_radius,
                                                         outer_radius= magnet_outer_radius,
                                                         height = magnet_height,
                                                         angle_rad= magnet_open_arc,
                                                         center_angle_rad= rotor_angle_offset + i*pole_arc,
                                                         z_offset= magnet_z_offset,
                                                         )
        sign = None
        if i%2 == 0:
            sign = 1
        else:
            sign = -1

        magnet_template = Segment(mesh = magnet_mesh,
                                  material= "magnet",
                                  magnet_source= magnet_source,
                                  magnetization_direction=np.array([0,0,sign]))
        if create_magnet == True:
            geometry.append(magnet_template)
    
    # create tooth tip 
    # component 1:
    z_tooth_tip_1 = motor.rotor_length + motor.magnet_length + motor.airgap
    z_tooth_tip_2 = z_tooth_tip_1 + motor.tooth_tip_depth
    
    C_in = motor.shaft_hole_diameter * pi
    C_in_per_slot = C_in / motor.slot_number
    C_in_1 = C_in_per_slot - motor.slot_opening
    angle_in_1 = 2*np.atan(C_in_1/motor.shaft_hole_diameter)

    arc_in_1 = create_arc(motor.shaft_hole_diameter/2,
                          start_rad= stator_angle_offset - angle_in_1/2,
                          end_rad=stator_angle_offset + angle_in_1/2)
    
    C_out = motor.stator_lam_dia * pi
    C_out_per_slot = C_out / motor.slot_number
    C_out_1 = C_out_per_slot - motor.slot_opening
    angle_out_1 = 2* np.atan(C_out_1 / motor.stator_lam_dia)
    arc_out_1 = create_arc(radius=  motor.stator_lam_dia/2,
                           start_rad= stator_angle_offset - angle_out_1/2,
                           end_rad= stator_angle_offset + angle_out_1/2)
    
    polygon1 = create_smart_polygon(arc1= arc_in_1,
                                    arc2= arc_out_1)
    
    mesh_1 = extrude_polygon_between_z(polygon = polygon1,
                                       z1=z_tooth_tip_1,
                                       z2=z_tooth_tip_2)
    
    for i in range(int(motor.slot_number)):
        mesh_rotated = rotate_mesh_z(mesh_1, i * 2* pi / motor.slot_number)
        tooth_tip_rotated = Segment(mesh=mesh_rotated,
                                    material="iron")
        if create_tooth == True:
            geometry.append(tooth_tip_rotated)
            

    # component 2 
    w1 = (1/2) * (motor.slot_width - motor.slot_opening)
    h1 = w1 * np.tan(np.radians(motor.tooth_tip_angle))
    z_tooth_tip_3 = z_tooth_tip_2 + h1
    C_in_2 = C_in_per_slot - motor.slot_width
    angle_in_2 = 2 * np.atan(C_in_2 / motor.stator_bore_dia)
    arc_in_2 = create_arc(radius= motor.stator_bore_dia /2,
                          start_rad= stator_angle_offset - angle_in_2/2,
                          end_rad= stator_angle_offset + angle_in_2/2)
    
    C_out_2 = C_out_per_slot -  motor.slot_width
    angle_out_2 = 2 * np.atan(C_out_2 / motor.stator_lam_dia)
    arc_out_2 = create_arc(radius= motor.stator_lam_dia/2,
                           start_rad= stator_angle_offset - angle_out_2/2,
                           end_rad= stator_angle_offset + angle_out_2/2)
    
    polygon2 = create_smart_polygon(arc1= arc_in_2,
                                    arc2= arc_out_2)
    
    mesh2 = create_frustum_loft(poly1 = polygon1,
                                poly2= polygon2,
                                z1 = z_tooth_tip_2,
                                z2 = z_tooth_tip_3)

    for i in range(int(motor.slot_number)):
        mesh2_rotated = rotate_mesh_z(mesh = mesh2,
                                      angle_rad= i * 2*pi / motor.slot_number)
        if create_tooth == True:
            geometry.append(Segment(mesh=mesh2_rotated,material="iron"))

    #create_tooth
    z_offset_4 = z_tooth_tip_2 + motor.slot_depth
    mesh_3 = extrude_polygon_between_z(polygon=polygon2,
                                       z1 = z_tooth_tip_3,
                                       z2= z_offset_4)
    
    for i in range(int(motor.slot_number)):
        mesh_3_rotated = rotate_mesh_z(mesh= mesh_3,
                                       angle_rad = i * 2 * pi / motor.slot_number)
        winding_vector = motor.winding_matrix[i]
        if create_tooth == True:
            geometry.append(Segment(mesh=mesh_3_rotated,
                                    material="iron",
                                    winding_vector = winding_vector))
        
    # create stator yoke
    stator_yoke_mesh = create_tube(inner_radius=motor.stator_bore_dia / 2,
                                   outer_radius=motor.stator_lam_dia /2,
                                   height = motor.stator_length - motor.tooth_tip_depth - motor.slot_depth,
                                   z_offset=z_offset_4)
    if create_stator_yoke == True:
        geometry.append(Segment(mesh = stator_yoke_mesh,
                                material="iron"))
    return Geometry(geometry=geometry)
