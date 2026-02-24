import numpy as np
import math
from src.core.motor_type.utils.for_create_geometry.rotate_point_z import rotate_point_z

def create_winding_section(m3d, section_radius, slot_index, slot_arc, offset_x, z):
    angle_i = (slot_index * slot_arc) + (slot_arc / 2)
    z_str = str(round(z, 2)).replace('.', '_')
    section_name = f"Section_S{slot_index}_Z{z_str}"
    
    if section_name in m3d.modeler.object_names:
        m3d.modeler.delete(section_name)
    
    m3d.modeler.create_circle(
        orientation="YZ",
        origin=[offset_x, 0, z],
        radius=section_radius,
        name=section_name,
        is_covered=True
    )
    m3d.modeler.rotate(assignment=section_name, axis="Z", angle=angle_i)
    return section_name

def get_arc_end_winding_points(r_arc, ang_start, ang_end, z_start, z_end, num_segments=15):
    pts = []
    diff = (ang_end - ang_start + 180) % 360 - 180
    for i in range(num_segments + 1):
        t = i / num_segments
        curr_ang = ang_start + t * diff
        curr_z = z_start + t * (z_end - z_start)
        x = r_arc * math.cos(math.radians(curr_ang))
        y = r_arc * math.sin(math.radians(curr_ang))
        pts.append([x, y, curr_z])
    return pts

def remove_duplicate_points(points, tolerance=1e-6):
    if not points: return []
    cleaned = [points[0]]
    for p in points[1:]:
        if np.linalg.norm(np.array(p) - np.array(cleaned[-1])) > tolerance:
            cleaned.append(p)
    return cleaned

def create_winding(motor, m3d):
    # 1. Trích xuất dữ liệu hình học
    st_geo = motor.geometry_data.stator
    ro_geo = motor.geometry_data.rotor
    slot_num = st_geo.slot_number
    st_lam_dia = st_geo.stator_lam_dia * 1e3
    st_bore_dia = st_geo.stator_bore_dia * 1e3
    sl_width, sl_depth = st_geo.slot_width * 1e3, st_geo.slot_depth * 1e3
    
    slot_arc = 360 / slot_num
    r_out, r_in = st_lam_dia / 2, st_bore_dia / 2
    r_avg = (r_in + r_out) / 2

    # 2. Dữ liệu dây quấn
    wdg_data = motor.winding_data
    sl_matrix = wdg_data.slot_matrix
    throw, phase, layers = int(wdg_data.throw), int(wdg_data.phase), int(wdg_data.winding_layer)
    
    # Khống chế bán kính dây dẫn
    wire_rad = min(sl_depth / (throw + 2), sl_width) * 0.4 * 0.5
    
    # Tọa độ Z với clearance
    offset_z0 = (ro_geo.rotor_length + ro_geo.magnet_length + ro_geo.airgap) * 1e3
    clearance = wire_rad * 1.2
    z_start_layer = offset_z0 + clearance
    z_end_layer = (offset_z0 + sl_depth) - clearance
    z_layers = np.linspace(z_start_layer, z_end_layer, layers).tolist() if layers > 1 else [z_start_layer]

    # HIỆU CHỈNH: Extension bằng 1.5 lần bán kính dây
    ext = 1.5 * wire_rad
    r_in_ext, r_out_ext = r_in - ext, r_out + ext
    
    # Bán kính cung tròn (đẩy ra thêm một đoạn nhỏ để không chạm vào phần extension)
    r_arc_in, r_arc_out = r_in_ext - 1.0, r_out_ext + 1.0

    if sl_matrix is not None:
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        
        for p_idx in range(phase):
            for s_idx in range(int(slot_num)):
                if sl_matrix[s_idx, p_idx] > 0:
                    t_idx = (s_idx + throw) % int(slot_num)
                    ang_s = (s_idx * slot_arc) + (slot_arc / 2)
                    ang_t = (t_idx * slot_arc) + (slot_arc / 2)

                    # Điểm mốc cạnh tác dụng
                    p1_in  = list(rotate_point_z([r_in_ext, 0, z_layers[0]], ang_s))
                    p1_out = list(rotate_point_z([r_out_ext, 0, z_layers[0]], ang_s))
                    p2_out = list(rotate_point_z([r_out_ext, 0, z_layers[1]], ang_t))
                    p2_in  = list(rotate_point_z([r_in_ext, 0, z_layers[1]], ang_t))
                    
                    # Điểm nối vào cung tròn
                    p1_out_arc_start = list(rotate_point_z([r_arc_out, 0, z_layers[0]], ang_s))
                    p2_out_arc_end   = list(rotate_point_z([r_arc_out, 0, z_layers[1]], ang_t))
                    p2_in_arc_start  = list(rotate_point_z([r_arc_in, 0, z_layers[1]], ang_t))
                    p1_in_arc_end    = list(rotate_point_z([r_arc_in, 0, z_layers[0]], ang_s))

                    coil_name = f"Coil_Ph{p_idx}_S{s_idx}"
                    path_name = f"{coil_name}_Path"
                    
                    if coil_name in m3d.modeler.object_names: m3d.modeler.delete(coil_name)
                    if path_name in m3d.modeler.object_names: m3d.modeler.delete(path_name)

                    # Gom điểm lộ trình
                    raw_points = []
                    raw_points.extend([p1_in, p1_out, p1_out_arc_start])
                    raw_points.extend(get_arc_end_winding_points(r_arc_out, ang_s, ang_t, z_layers[0], z_layers[1], 15))
                    raw_points.extend([p2_out_arc_end, p2_out, p2_in, p2_in_arc_start])
                    raw_points.extend(get_arc_end_winding_points(r_arc_in, ang_t, ang_s, z_layers[1], z_layers[0], 15))
                    raw_points.append(p1_in)

                    # Lọc điểm trùng lặp tránh lỗi CreatePolyline
                    full_path_points = remove_duplicate_points(raw_points)

                    m3d.modeler.create_polyline(
                        points=full_path_points,
                        name=path_name,
                        close_surface=False,
                        xsection_type=None
                    )
                    
                    section_name = create_winding_section(m3d, wire_rad, s_idx, slot_arc, r_avg, z_layers[0])
                    m3d.modeler.sweep_along_path(assignment=section_name, sweep_object=path_name)
                    
                    m3d.modeler[section_name].name = coil_name
                    m3d.assign_material(assignment=coil_name, material="copper")
                    m3d.modeler[coil_name].color = colors[p_idx % 3]
                    m3d.modeler[coil_name].transparency = 0.2