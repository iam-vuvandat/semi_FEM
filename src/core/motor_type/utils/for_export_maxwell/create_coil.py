import numpy as np
import math
from src.core.motor_type.utils.for_create_geometry.rotate_point_z import rotate_point_z
from src.core.motor_type.utils.for_export_maxwell.create_conductor import create_conductor

def get_semi_circle_points(p_start, p_end, num_segments=15):
    p_s = np.array(p_start)
    p_e = np.array(p_end)
    mid = (p_s + p_e) / 2
    vec = p_e - p_s
    dist = np.linalg.norm(vec)
    r_vec = mid.copy()
    r_vec[2] = 0
    side = r_vec / np.linalg.norm(r_vec) if np.linalg.norm(r_vec) > 1e-9 else np.array([0, 1, 0])
    points = []
    for i in range(num_segments + 1):
        theta = (i / num_segments) * math.pi
        p = p_s * (1 - i/num_segments) + p_e * (i/num_segments)
        p = p + side * (math.sin(theta) * dist * 0.4)
        points.append(p.tolist())
    return points

def create_coil(m3d, p1, p2, p3, p4, width=4.0, conductors_number=10, flare_offset=8.0):
    def get_flared_jog_anchors(pa, pb, offset_val):
        va, vb = np.array(pa), np.array(pb)
        m = (va + vb) / 2
        
        # Tinh toan diem p_m1, p_m2 ban dau (chua choai)
        ratio = 0.2
        pm1 = m - (vb - va) * (ratio / 2)
        pm2 = m + (vb - va) * (ratio / 2)
        
        # Thuc hien "choai" theo phuong huong tam (Radial)
        def apply_flare(p, off):
            r_vec = np.array([p[0], p[1], 0])
            norm = np.linalg.norm(r_vec)
            if norm < 1e-9: return p
            return (p + (r_vec / norm) * off).tolist()

        return apply_flare(pm1, offset_val), apply_flare(pm2, offset_val)

    # pm_o1, pm_o2: Choai ra ngoai (flare_offset duong)
    pm_o1, pm_o2 = get_flared_jog_anchors(p2, p3, flare_offset) 
    # pm_i1, pm_i2: Choai vao trong (flare_offset am)
    pm_i1, pm_i2 = get_flared_jog_anchors(p4, p1, -flare_offset)

    segments_config = [
        ([pm_i2, p1, p2, pm_o1], False),       
        (get_semi_circle_points(pm_o1, pm_o2), False), 
        ([pm_o2, p3, p4, pm_i1], False),       
        (get_semi_circle_points(pm_i1, pm_i2), True)   
    ]
    
    all_solids = []
    terminal_rect = None
    for path, is_term in segments_config:
        res_solid, res_terminal = create_conductor(m3d=m3d, point_list=path, width=width, create_terminal=is_term)
        all_solids.append(res_solid)
        if is_term: terminal_rect = res_terminal
            
    if len(all_solids) > 1:
        m3d.modeler.unite(all_solids)
    
    final_solid = all_solids[0]
    coil_terminal_obj = m3d.assign_coil(assignment=terminal_rect, conductors_number=conductors_number)
    
    return final_solid, coil_terminal_obj