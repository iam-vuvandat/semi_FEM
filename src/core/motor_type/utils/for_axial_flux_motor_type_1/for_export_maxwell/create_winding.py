import numpy as np
import math
from src.core.motor_type.utils.for_create_geometry.rotate_point_z import rotate_point_z

def create_winding(motor, m3d):
    # 1. Trích xuất dữ liệu hình học
    st_geo = motor.geometry_data.stator
    ro_geo = motor.geometry_data.rotor
    
    slot_num        = st_geo.slot_number
    st_lam_dia      = st_geo.stator_lam_dia * 1e3
    st_bore_dia     = st_geo.stator_bore_dia * 1e3
    sl_width        = st_geo.slot_width * 1e3
    sl_opening      = st_geo.slot_opening * 1e3
    sl_depth        = st_geo.slot_depth * 1e3
    t_tip_depth     = st_geo.tooth_tip_depth * 1e3
    t_tip_angle     = st_geo.tooth_tip_angle
    
    ro_len          = ro_geo.rotor_length * 1e3
    mg_len          = ro_geo.magnet_length * 1e3
    ag              = ro_geo.airgap * 1e3

    offset_z0       = ro_len + mg_len + ag
    z_top           = offset_z0 + t_tip_depth + (sl_width - sl_opening) * 0.5 * np.tan(np.radians(t_tip_angle))
    z_yoke          = offset_z0 + t_tip_depth + sl_depth
    slot_arc        = 360 / slot_num
    r_out           = st_lam_dia / 2
    r_in            = st_bore_dia / 2

    # 2. Dữ liệu dây quấn
    wdg_data        = motor.winding_data
    sl_matrix       = wdg_data.slot_matrix
    throw           = int(wdg_data.throw)
    phase           = int(wdg_data.phase)
    layers          = int(wdg_data.winding_layer)
    
    delta_z         = (z_yoke - z_top) / (layers + 1)
    wire_rad        = np.min([sl_width, delta_z]) * 0.25 * 0.82 

    z_layers = [z_top + (i+1)*delta_z for i in range(layers)]
    in_dist, out_dist = r_in - 4*wire_rad, r_out + 4*wire_rad

    # 3. Tính toán ma trận điểm active side
    active_side = np.zeros((layers, int(slot_num), 2, 3))
    for i in range(layers):
        p_in_ref, p_out_ref = rotate_point_z([in_dist, 0, z_layers[i]], slot_arc/2), rotate_point_z([out_dist, 0, z_layers[i]], slot_arc/2)
        for j in range(int(slot_num)):
            active_side[i,j,0] = rotate_point_z(p_in_ref, j*slot_arc)
            active_side[i,j,1] = rotate_point_z(p_out_ref, j*slot_arc)

    if sl_matrix is not None:
        z_mid, colors = np.mean(z_layers), [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        
        for p_idx in range(phase):
            for s_idx in range(int(slot_num)):
                if sl_matrix[s_idx, p_idx] > 0:
                    t_idx = (s_idx + throw) % int(slot_num)
                    p1, p2, p3, p4 = list(active_side[0, s_idx, 0]), list(active_side[0, s_idx, 1]), list(active_side[1, t_idx, 1]), list(active_side[1, t_idx, 0])
                    m_theta = (s_idx + throw/2)*slot_arc + slot_arc/2
                    pm_out = list(rotate_point_z([out_dist + wire_rad, 0, z_mid], m_theta))
                    pm_in  = list(rotate_point_z([in_dist - wire_rad, 0, z_mid], m_theta))
                    
                    coil_name = f"Coil_Ph{p_idx}_S{s_idx}"
                    if coil_name in m3d.modeler.object_names: m3d.modeler.delete(coil_name)

                    segments = []
                    s1 = m3d.modeler.create_polyline([p1, p2], name=f"{coil_name}_s1", xsection_type="Circle", xsection_width=2*wire_rad)
                    segments.append(s1.name)
                    s2 = m3d.modeler.create_polyline([p2, pm_out, p3], segment_type="Arc", name=f"{coil_name}_s2", xsection_type="Circle", xsection_width=2*wire_rad)
                    segments.append(s2.name)
                    s3 = m3d.modeler.create_polyline([p3, p4], name=f"{coil_name}_s3", xsection_type="Circle", xsection_width=2*wire_rad)
                    segments.append(s3.name)
                    s4 = m3d.modeler.create_polyline([p4, pm_in, p1], segment_type="Arc", name=f"{coil_name}_s4", xsection_type="Circle", xsection_width=2*wire_rad)
                    segments.append(s4.name)

                    m3d.modeler.unite(assignment=segments)
                    m3d.modeler[segments[0]].name = coil_name
                    
                    # Gán vật liệu Copper
                    m3d.modeler[coil_name].material_name = "copper"
                    
                    # Debug Volume
                    coil_volume = m3d.modeler[coil_name].volume
                    print(f"DEBUG: {coil_name} united. Volume: {coil_volume:.4f} mm3")
                    
                    m3d.modeler[coil_name].color = colors[p_idx % 3]
                    m3d.modeler[coil_name].transparency = 0.2