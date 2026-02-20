import paths
import os
import time
import glob
from pyaedt import Maxwell3d
import paths 
import numpy as np
import math 
pi = math.pi

from src.core.motor_type.utils.for_create_geometry.rotate_point_z import rotate_point_z

def export_to_maxwell(motor):
    
    # Collect Gabages
    os.system("taskkill /F /IM ansysedt.exe /T")
    os.system("taskkill /F /IM AnsysGRPC.exe /T")

    ansoft_dir = r"C:\Users\Surface\Documents\Ansoft"
    for f in glob.glob(os.path.join(ansoft_dir, "*.aedt.auto")):
        try: os.remove(f)
        except: pass
    time.sleep(1)

    # Open Maxwell 3D & Save Project
    m3d = Maxwell3d(version="2023.1", new_desktop=True, non_graphical=False)
    

    project_root = paths.configure_path()
    save_path = os.path.join(project_root, "Ansys_Projects")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    project_name = os.path.join(save_path, "pyAEDT_test.aedt")
    m3d.save_project(project_name)

    time.sleep(1)
    m3d.solution_type = "Transient"
    m3d.change_material_override(True)

    # Draw geometry

    # geometry parameter 
    ## Rotor, unit: mm
    rotor = motor.geometry_data.rotor
    pole_number          = rotor.pole_number 
    rotor_lam_dia        = rotor.rotor_lam_dia  * 1e3 # (m-> mm)
    magnet_arc           = rotor.magnet_arc # (Deg)
    magnet_embed_depth   = rotor.magnet_embed_depth  
    magnet_depth         = rotor.magnet_depth * 1e3 
    magnet_segments      = rotor.magnet_segments
    banding_depth        = rotor.banding_depth
    shaft_dia            = rotor.shaft_dia *1e3
    shaft_hole_diameter  = rotor.shaft_hole_diameter *1e3 
    airgap               = rotor.airgap *1e3
    magnet_length        = rotor.magnet_length *1e3
    rotor_length         = rotor.rotor_length *1e3

    ## Rotor

    rotor_outer_radius = rotor_lam_dia / 2 
    rotor_inner_radius = shaft_hole_diameter / 2

    rotor_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=rotor_outer_radius, height=rotor_length)
    rotor_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=rotor_inner_radius, height=rotor_length)
    m3d.modeler.subtract(blank_list=[rotor_base], tool_list=[rotor_hole], keep_originals=False)
    m3d.modeler[rotor_base].material_name = "steel_1008"
    m3d.modeler[rotor_base].name = "rotor_yoke"

    ## Magnet
    magnet_radius = rotor_outer_radius - magnet_embed_depth
    magnet_hole   = magnet_radius - magnet_depth

    magnet_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, rotor_length], radius=magnet_radius, height=magnet_length)
    magnet_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, rotor_length], radius=magnet_hole, height=magnet_length)
    m3d.modeler.subtract(blank_list=[magnet_base], tool_list=[magnet_hole], keep_originals=False)

    ## Knife for split magnet
    pole_arc = 360 / pole_number
    magnet_arc_mechanical = pole_arc * (magnet_arc/180)
    half_magnet_arc_mechanical = magnet_arc_mechanical / 2 

    knife_1 = m3d.modeler.create_box(origin=[0, 0, rotor_length], sizes=[magnet_radius, 0.0001, magnet_length])
    m3d.modeler.rotate(knife_1, axis="Z", angle=half_magnet_arc_mechanical)
    knife_2 = m3d.modeler.create_box(origin=[0, 0, rotor_length], sizes=[magnet_radius, 0.0001, magnet_length])
    m3d.modeler.rotate(knife_2, axis="Z", angle=-half_magnet_arc_mechanical)
    m3d.modeler.subtract(blank_list=[magnet_base], tool_list=[knife_1, knife_2], keep_originals=False)
    magnet_segments = m3d.modeler.separate_bodies(magnet_base)

    if magnet_segments[0].volume >= magnet_segments[1].volume:
        m3d.modeler.delete(magnet_segments[0])
        magnet_pole = magnet_segments[1]
    else:
        m3d.modeler.delete(magnet_segments[1])
        magnet_pole = magnet_segments[0]

    m3d.modeler[magnet_pole].name = "magnet_pole"
    mat_n = m3d.materials.add_material("NdFe30_N")
    mat_n.set_magnetic_coercivity(-838000, 0, 0, 1)
    mat_s = m3d.materials.add_material("NdFe30_S")
    mat_s.set_magnetic_coercivity(-838000, 0, 0, -1)
    m3d.modeler[magnet_pole].material_name = "NdFe30_N"

    arc_pole = 360 / pole_number
    _, new_pole = m3d.modeler.duplicate_around_axis(assignment=magnet_pole, axis="Z", angle = arc_pole, clones=pole_number)
    for i in range(len(new_pole)):
        m3d.modeler[new_pole[i]].material_name = "NdFe30_S" if i % 2 == 0 else "NdFe30_N"

    ## Moving band for Rotor

    moving_band = m3d.modeler.create_cylinder(
        orientation="Z", 
        origin=[0, 0, - rotor_length], 
        radius= rotor_outer_radius * 1.1, 
        height= 2 * rotor_length + magnet_length + airgap * 0.5
    )

    m3d.modeler[moving_band].name = "moving_band"
    m3d.modeler[moving_band].material_name = "vacuum"
    motion_setup = m3d.assign_rotate_motion(assignment="moving_band", angular_velocity="1500rpm")
    motion_setup.props["BandMappingAngle"] = "1deg"

    rotating_parts = ["rotor_yoke", "magnet_pole"] + new_pole
    m3d.eddy_effects_on(rotating_parts, enable_eddy_effects=False)

    ## Stator

    ## Stator, unit: mm
    stator = motor.geometry_data.stator
    slot_number         = stator.slot_number
    stator_lam_dia      = stator.stator_lam_dia *1e3
    stator_bore_dia     = stator.stator_bore_dia  *1e3
    slot_opening        = stator.slot_opening   *1e3
    wdg_extension_inner = stator.wdg_extension_inner   *1e3
    wdg_extension_outer = stator.wdg_extension_outer   *1e3
    slot_width          = stator.slot_width  *1e3
    slot_depth          = stator.slot_depth  *1e3
    slot_corner_radius  = stator.slot_corner_radius  
    tooth_tip_depth     = stator.tooth_tip_depth   *1e3
    tooth_tip_angle     = stator.tooth_tip_angle
    stator_length       = stator.stator_length  *1e3

    offset_z0 = rotor_length + magnet_length + airgap
    stator_outer_radius = stator_lam_dia / 2 
    stator_inner_radius = stator_bore_dia / 2

    ### tooth tip 1 
    tooth_tip_1_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, offset_z0], radius=stator_outer_radius, height=tooth_tip_depth)
    tooth_tip_1_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, offset_z0], radius=stator_inner_radius, height=tooth_tip_depth)
    m3d.modeler.subtract(blank_list=[tooth_tip_1_base], tool_list=[tooth_tip_1_hole], keep_originals=False)
    m3d.modeler[tooth_tip_1_base].material_name = "steel_1008"

    slot_arc = 360 / slot_number
    half_slot_opening = slot_opening / 2

    knife_1 = m3d.modeler.create_box(origin=[0, -half_slot_opening, offset_z0], sizes=[stator_outer_radius * 1.5, slot_opening, tooth_tip_depth])
    m3d.modeler.rotate(knife_1, axis="Z", angle=slot_arc / 2)

    knife_2 = m3d.modeler.create_box(origin=[0, -half_slot_opening, offset_z0], sizes=[stator_outer_radius * 1.5, slot_opening, tooth_tip_depth])
    m3d.modeler.rotate(knife_2, axis="Z", angle=-slot_arc / 2)

    m3d.modeler.subtract(blank_list=[tooth_tip_1_base], tool_list=[knife_1, knife_2], keep_originals=False)
    tooth_tip_segments = m3d.modeler.separate_bodies(tooth_tip_1_base)

    if tooth_tip_segments[0].volume <= tooth_tip_segments[1].volume:
        m3d.modeler.delete(tooth_tip_segments[1])
        tooth_tip_1 = tooth_tip_segments[0]
    else:
        m3d.modeler.delete(tooth_tip_segments[0])
        tooth_tip_1 = tooth_tip_segments[1]
    m3d.modeler[tooth_tip_1].name = "tooth_tip_1"

    ### tooth_tip_2 (Sử dụng Arc mặc định)
    z_bottom_surface = offset_z0 + tooth_tip_depth
    w1 = (1/2) * (slot_width - slot_opening)
    h1 = w1 * np.tan(np.radians(tooth_tip_angle))
    z_top_surface = z_bottom_surface + h1

    C_in_per_slot = (stator_bore_dia * np.pi) / slot_number
    angle_in_mouth = 2 * np.arctan((C_in_per_slot - slot_opening) / stator_bore_dia)
    angle_out_mouth = 2 * np.arctan(((stator_lam_dia * np.pi / slot_number) - slot_opening) / stator_lam_dia)

    # Vẽ mặt đáy (Sheet Bottom) bằng 3 điểm Arc mặc định
    p1_in_b = [stator_bore_dia/2 * np.cos(-angle_in_mouth/2), stator_bore_dia/2 * np.sin(-angle_in_mouth/2), z_bottom_surface]
    p2_in_b = [stator_bore_dia/2, 0, z_bottom_surface]
    p3_in_b = [stator_bore_dia/2 * np.cos(angle_in_mouth/2), stator_bore_dia/2 * np.sin(angle_in_mouth/2), z_bottom_surface]
    arc_in_b = m3d.modeler.create_polyline(points=[p1_in_b, p2_in_b, p3_in_b], segment_type="Arc")

    p1_out_b = [stator_lam_dia/2 * np.cos(-angle_out_mouth/2), stator_lam_dia/2 * np.sin(-angle_out_mouth/2), z_bottom_surface]
    p2_out_b = [stator_lam_dia/2, 0, z_bottom_surface]
    p3_out_b = [stator_lam_dia/2 * np.cos(angle_out_mouth/2), stator_lam_dia/2 * np.sin(angle_out_mouth/2), z_bottom_surface]
    arc_out_b = m3d.modeler.create_polyline(points=[p1_out_b, p2_out_b, p3_out_b], segment_type="Arc")

    res_b = m3d.modeler.connect([arc_in_b, arc_out_b])
    bottom_sheet = res_b[0] if isinstance(res_b, list) else res_b

    # Vẽ mặt đỉnh (Sheet Top) bằng 3 điểm Arc mặc định
    angle_in_slot = 2 * np.arctan((C_in_per_slot - slot_width) / stator_bore_dia)
    angle_out_slot = 2 * np.arctan(((stator_lam_dia * np.pi / slot_number) - slot_width) / stator_lam_dia)

    p1_in_t = [stator_bore_dia/2 * np.cos(-angle_in_slot/2), stator_bore_dia/2 * np.sin(-angle_in_slot/2), z_top_surface]
    p2_in_t = [stator_bore_dia/2, 0, z_top_surface]
    p3_in_t = [stator_bore_dia/2 * np.cos(angle_in_slot/2), stator_bore_dia/2 * np.sin(angle_in_slot/2), z_top_surface]
    arc_in_t = m3d.modeler.create_polyline(points=[p1_in_t, p2_in_t, p3_in_t], segment_type="Arc")

    p1_out_t = [stator_lam_dia/2 * np.cos(-angle_out_slot/2), stator_lam_dia/2 * np.sin(-angle_out_slot/2), z_top_surface]
    p2_out_t = [stator_lam_dia/2, 0, z_top_surface]
    p3_out_t = [stator_lam_dia/2 * np.cos(angle_out_slot/2), stator_lam_dia/2 * np.sin(angle_out_slot/2), z_top_surface]
    arc_out_t = m3d.modeler.create_polyline(points=[p1_out_t, p2_out_t, p3_out_t], segment_type="Arc")

    res_t = m3d.modeler.connect([arc_in_t, arc_out_t])
    top_sheet = res_t[0] if isinstance(res_t, list) else res_t

    res_tip2 = m3d.modeler.connect([bottom_sheet, top_sheet])
    tooth_tip_2 = res_tip2[0] if isinstance(res_tip2, list) else res_tip2
    m3d.modeler[tooth_tip_2].name = "tooth_tip_2"
    m3d.modeler[tooth_tip_2].material_name = "steel_1008"

    ### tooth_body
    tooth_body_length = slot_depth - h1
    all_faces_tip2 = m3d.modeler.get_object_faces("tooth_tip_2")
    top_face_id = None
    z_max_tip2 = -1e9
    for f_id in all_faces_tip2:
        v_ids = m3d.modeler.get_face_vertices(f_id)
        if v_ids:
            z_pos = m3d.modeler.get_vertex_position(v_ids[0])
            if z_pos[2] > z_max_tip2:
                z_max_tip2 = z_pos[2]
                top_face_id = f_id

    res_body_sheet = m3d.modeler.create_object_from_face(assignment=top_face_id)
    body_sheet = res_body_sheet[0] if isinstance(res_body_sheet, list) else res_body_sheet

    sweep_body = m3d.modeler.sweep_along_vector(assignment=body_sheet, sweep_vector=[0, 0, tooth_body_length])
    tooth_body = sweep_body[0] if isinstance(sweep_body, list) else sweep_body
    m3d.modeler[tooth_body].name = "tooth_body"
    m3d.modeler[tooth_body].material_name = "steel_1008"

    # --- Nhân bản cụm răng (Không sử dụng Unite) ---
    m3d.modeler.duplicate_around_axis(
        assignment=["tooth_tip_1", "tooth_tip_2", "tooth_body"],
        axis="Z",
        angle=slot_arc,
        clones=slot_number
    )

    ### stator yoke
    yoke_height = stator_length - tooth_tip_depth - slot_depth
    z_yoke = offset_z0 + tooth_tip_depth + slot_depth

    stator_yoke = m3d.modeler.create_cylinder(
        orientation="Z", 
        origin=[0, 0, z_yoke], 
        radius=stator_outer_radius, 
        height=yoke_height
    )

    stator_yoke_hole = m3d.modeler.create_cylinder(
        orientation="Z", 
        origin=[0, 0, z_yoke], 
        radius=stator_inner_radius, 
        height=yoke_height
    )

    m3d.modeler.subtract(blank_list=[stator_yoke], tool_list=[stator_yoke_hole], keep_originals=False)
    m3d.modeler[stator_yoke].name = "stator_yoke"
    m3d.modeler[stator_yoke].material_name = "steel_1008"

    # Winding
    winding_data = motor.winding_data
    slot_winding = winding_data.slot_winding
    slot_matrix = winding_data.slot_matrix
    throw = int(winding_data.throw)
    phase = int(winding_data.phase)
    layer_number = int(winding_data.winding_layer)
    
    z_tooth_begin = z_top_surface
    z_tooth_end = z_yoke
    tooth_body_length = z_tooth_end - z_tooth_begin

    delta_z_layer = tooth_body_length / (layer_number + 1)
    z_layer_winding = np.zeros(layer_number)
    winding_section_radius = np.min([slot_width, delta_z_layer]) * (1/2) * (1/2)

    for i in range(layer_number):
        z_layer_winding[i] = z_tooth_begin + (i+1) * delta_z_layer

    inner_distance = stator_inner_radius - 4 * winding_section_radius
    outer_distance = stator_outer_radius + 4 * winding_section_radius

    inner_point = []
    outer_point = []
    for i in range(layer_number):
        inner_point.append(rotate_point_z(point=[inner_distance, 0, z_layer_winding[i]], theta_deg=slot_arc/2))
        outer_point.append(rotate_point_z(point=[outer_distance, 0, z_layer_winding[i]], theta_deg=slot_arc/2))

    active_side = np.zeros((layer_number, int(slot_number), 2, 3)) 

    for i in range(layer_number):
        for j in range(int(slot_number)):
            for k in range(2):
                if k == 0:
                    active_side[i,j,k] = rotate_point_z(point=inner_point[i], theta_deg=j * slot_arc)
                else:
                    active_side[i,j,k] = rotate_point_z(point=outer_point[i], theta_deg=j * slot_arc)

    # 1. Tạo các thanh dẫn rời (Conductors)
    conductors = [[None for _ in range(layer_number)] for _ in range(int(slot_number))]
    for j in range(int(slot_number)):
        for i in range(layer_number):
            p_start = active_side[i, j, 0]
            p_end = active_side[i, j, 1]
            line_name = f"Conductor_S{j}_L{i}"
            line_obj = m3d.modeler.create_polyline(
                points=[list(p_start), list(p_end)], 
                name=line_name
            )
            conductors[j][i] = line_obj

    # 2. Tạo kết nối bối dây gộp (Merged 1D Polyline)
    if slot_matrix is not None:
        z_mid = np.mean(z_layer_winding)
        for p_idx in range(phase):
            for s_idx in range(int(slot_number)):
                if slot_matrix[s_idx, p_idx] > 0:
                    target_s_idx = (s_idx + throw) % int(slot_number)
                    
                    p1 = active_side[0, s_idx, 0]        # Inner start, Layer 0
                    p2 = active_side[0, s_idx, 1]        # Outer end, Layer 0
                    p3 = active_side[1, target_s_idx, 1] # Outer end, Layer 1
                    p4 = active_side[1, target_s_idx, 0] # Inner start, Layer 1
                    
                    mid_theta = (s_idx + throw/2) * slot_arc
                    p_mid_outer = rotate_point_z(point=[outer_distance + winding_section_radius, 0, z_mid], 
                                                theta_deg=mid_theta + slot_arc/2)
                    p_mid_inner = rotate_point_z(point=[inner_distance - winding_section_radius, 0, z_mid], 
                                                theta_deg=mid_theta + slot_arc/2)
                    
                    line_name = f"Path_Ph{p_idx}_S{s_idx}"
                    
                    # Lệnh gộp tất cả điểm vào 1 đối tượng duy nhất
                    m3d.modeler.create_polyline(
                        points=[list(p1), list(p2), list(p_mid_outer), list(p3), list(p4), list(p_mid_inner)],
                        name=line_name,
                        close_surface=True
                    )

    
    


                    
    # Outer Region
    region = m3d.modeler.create_region(pad_value=30, pad_type="Percentage Offset")
    m3d.assign_insulating(assignment=[region])

    # Mesh
    all_objects = m3d.modeler.object_names
    mesh_targets = [
        obj for obj in all_objects 
        if obj != region              
        and "Line" not in obj        
        and "Sheet" not in obj      
    ]

    maximum_element_length = magnet_length *2 
    m3d.mesh.assign_length_mesh(
        assignment=mesh_targets,
        maximum_length=f"{maximum_element_length}mm",
        maximum_elements=None,
        name="Global_Core_Mesh"
    )

    # Setup Analysis
    setup_name = "Setup1"

    if setup_name in m3d.setup_names:
        m3d.delete_setup(setup_name)

    
    setup = m3d.create_setup(name=setup_name, setup_type="Transient")

    
    setup.props["StopTime"] = "10ms"
    setup.props["TimeStep"] = "2ms"

    
    setup.props["SaveFieldsType"] = "Every N Steps"
    setup.props["N Steps"] = "1"
    setup.props["Steps From"] = "0s"
    setup.props["Steps To"] = "10ms"


    setup.props["NonlinearSolverResidual"] = "0.005"
    setup.props["ScalarPotential"] = "Second Order"
    setup.props["SmoothBHCurve"] = False

    setup.update()
    m3d.save_project()

    # Run
    #m3d.analyze_setup(setup_name)

    return None

if __name__ == "__main__":
    from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
    motor = AxialFluxMotorType1()
    motor.export_to_maxwell()
