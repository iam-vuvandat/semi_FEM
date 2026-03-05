from dataclasses import dataclass, field
import numpy as np
import trimesh
from typing import Optional, Any

@dataclass
class ElementInfo:
    material: str = "air"
    magnet_source: float = 0.0
    magnetization_direction: np.ndarray = field(default_factory=lambda: np.array([0., 0., 1.]))
    winding_vector: np.ndarray = field(default_factory=lambda: np.array([0., 0., 0.]))
    winding_normal: np.ndarray = field(default_factory=lambda: np.array([0., 0., 1.]))
    volume_error: float = 0.0
    
    coordinate: np.ndarray = field(default_factory=lambda: np.zeros((2, 3)))
    dimension: np.ndarray = field(default_factory=lambda: np.zeros((2, 3)))

def extract_element_info(position: tuple, 
                         geometry: Any, 
                         mesh: Any) -> Optional[ElementInfo]:
    
    if not isinstance(position, (tuple, list)) or len(position) != 3:
        raise TypeError("Position phải là tuple (i_r, i_t, i_z)")

    i_r, i_t, i_z = position
    r_nodes, t_nodes, z_nodes = mesh.r_nodes, mesh.theta_nodes, mesh.z_nodes

    if not (0 <= i_r < len(r_nodes) - 1): return None
    if not (0 <= i_t < len(t_nodes) - 1): return None
    if not (0 <= i_z < len(z_nodes) - 1): return None

    # --- 1. TINH TOAN TOA DO ---
    r_i, r_next = float(r_nodes[i_r]), float(r_nodes[i_r+1])
    t_j, t_next = float(t_nodes[i_t]), float(t_nodes[i_t+1])
    z_k, z_next = float(z_nodes[i_z]), float(z_nodes[i_z+1])

    r_avg = (r_i + r_next) / 2.0
    t_avg = (t_j + t_next) / 2.0
    z_avg = (z_k + z_next) / 2.0

    center_x = r_avg * np.cos(t_avg)
    center_y = r_avg * np.sin(t_avg)
    center_z = z_avg
    center_point = np.array([[center_x, center_y, center_z]])

    coord_array = np.array([[r_i, t_j, z_k], [r_next, t_next, z_next]])

    # --- 2. DIMENSION CUA ELEMENT (GIONG BAN CU) ---
    d_r = abs(r_next - r_i)
    d_t = abs(t_next - t_j) 
    d_z = abs(z_next - z_k)
    row_element = [d_r, d_t, d_z] 

    # --- 3. KIEM TRA VA CHAM (POINT-IN-MESH) ---
    segments_list = geometry.geometry if hasattr(geometry, 'geometry') else geometry
    dominant_segment = None

    for seg in segments_list:
        if not hasattr(seg, 'mesh') or seg.mesh is None: 
            continue
        
        seg_bounds = seg.mesh.bounds
        if not (np.all(center_point[0] > seg_bounds[0]) and np.all(center_point[0] < seg_bounds[1])):
            continue

        if seg.mesh.contains(center_point):
            dominant_segment = seg
            break 

    # --- 4. TRICH XUAT THUOC TINH ---
    def get_vec(obj, attr):
        val = getattr(obj, attr, None)
        return np.array(val, dtype=float) if val is not None else np.array([0., 0., 0.])

    def safe_float(obj, attr, default_val):
        val = getattr(obj, attr, None)
        return float(val) if val is not None else default_val

    if dominant_segment:
        if hasattr(dominant_segment, 'dimension') and dominant_segment.dimension is not None:
             row_segment = dominant_segment.dimension
        else:
             row_segment = [safe_float(dominant_segment, "r_length", d_r),
                            safe_float(dominant_segment, "t_length", d_t), 
                            safe_float(dominant_segment, "z_length", d_z)]
    else:
        row_segment = row_element

    dims_array = np.array([row_element, row_segment], dtype=float)

    # --- 5. RETURN ---
    if dominant_segment is None:
        return ElementInfo(
            material="air",
            coordinate=coord_array,
            dimension=dims_array
        )

    return ElementInfo(
        material=dominant_segment.material,
        magnet_source=safe_float(dominant_segment, "magnet_source", 0.0),
        magnetization_direction=get_vec(dominant_segment, "magnetization_direction"),
        winding_vector=get_vec(dominant_segment, "winding_vector"),
        winding_normal=get_vec(dominant_segment, "winding_normal"),
        coordinate=coord_array,
        dimension=dims_array
    )