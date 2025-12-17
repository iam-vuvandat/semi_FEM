from dataclasses import dataclass, field
import numpy as np
import trimesh
from collections import defaultdict
from typing import Optional, List, Any

@dataclass
class ElementInfo:
    material: str = "air"
    magnet_source: float = 0.0
    magnetization_direction: np.ndarray = field(default_factory=lambda: np.array([0., 0., 1.]))
    winding_vector: np.ndarray = field(default_factory=lambda: np.array([0., 0., 0.]))
    winding_normal: np.ndarray = field(default_factory=lambda: np.array([0., 0., 1.]))
    
    # --- COORDINATE (2x3) ---
    # Row 0: Start Coordinate [r_i, t_j, z_k]
    # Row 1: End Coordinate   [r_i+1, t_j+1, z_k+1]
    coordinate: np.ndarray = field(default_factory=lambda: np.zeros((2, 3)))

    # --- DIMENSION (2x3) ---
    # Col 0: r (radial length)
    # Col 1: theta (angle in radians)
    # Col 2: z (axial length)
    # Row 0: Element Info (Voxel size)
    # Row 1: Segment Info (Geometry size)
    dimension: np.ndarray = field(default_factory=lambda: np.zeros((2, 3)))

def extract_element_info(position: tuple, geometry: Any, mesh: Any) -> Optional[ElementInfo]:
    if not isinstance(position, (tuple, list)) or len(position) != 3:
        raise TypeError("Position phải là tuple (i_r, i_t, i_z)")

    i_r, i_t, i_z = position
    r_nodes, t_nodes, z_nodes = mesh.r_nodes, mesh.theta_nodes, mesh.z_nodes

    if not (0 <= i_r < len(r_nodes) - 1): return None
    if not (0 <= i_t < len(t_nodes) - 1): return None
    if not (0 <= i_z < len(z_nodes) - 1): return None

    # --- 1. COORDINATE ---
    r_i, r_next = float(r_nodes[i_r]), float(r_nodes[i_r+1])
    t_j, t_next = float(t_nodes[i_t]), float(t_nodes[i_t+1])
    z_k, z_next = float(z_nodes[i_z]), float(z_nodes[i_z+1])

    coord_array = np.array([
        [r_i, t_j, z_k],
        [r_next, t_next, z_next]
    ])

    # --- 2. ELEMENT DIMENSIONS (Row 0) ---
    d_r = abs(r_next - r_i)
    d_t = abs(t_next - t_j) # Góc mở (Radian)
    d_z = abs(z_next - z_k)
    
    # Tính độ dài cung để tạo Box vật lý cho việc check giao cắt (Intersection)
    r_avg = (r_i + r_next) / 2.0
    grid_arc_len = r_avg * d_t 

    # --- 3. VOXEL INTERSECTION CHECK ---
    t_avg = (t_j + t_next) / 2.0
    z_avg = (z_k + z_next) / 2.0
    
    center_x = r_avg * np.cos(t_avg)
    center_y = r_avg * np.sin(t_avg)
    center_z = z_avg

    # Box vật lý dùng mét (cho trimesh)
    voxel_dims = [d_r, grid_arc_len, d_z]
    voxel_mesh = trimesh.creation.box(extents=voxel_dims)

    rotation_matrix = trimesh.transformations.rotation_matrix(t_avg, [0, 0, 1])
    translation_matrix = trimesh.transformations.translation_matrix([center_x, center_y, center_z])
    final_transform = trimesh.transformations.concatenate_matrices(translation_matrix, rotation_matrix)
    voxel_mesh.apply_transform(final_transform)
    
    total_voxel_volume = voxel_mesh.volume
    vox_bounds = voxel_mesh.bounds 

    # --- 4. FIND DOMINANT SEGMENT ---
    segments_list = geometry.geometry if hasattr(geometry, 'geometry') else geometry
    segment_volumes = {}
    material_volumes = defaultdict(float)
    occupied_volume = 0.0

    for seg in segments_list:
        if not hasattr(seg, 'mesh') or seg.mesh is None: continue
        
        seg_bounds = seg.mesh.bounds
        if not (np.all(vox_bounds[1] > seg_bounds[0]) and np.all(vox_bounds[0] < seg_bounds[1])):
            continue
            
        try:
            intersection = trimesh.boolean.intersection([voxel_mesh, seg.mesh])
            if intersection.is_volume:
                vol = intersection.volume
                if vol > 1e-12:
                    segment_volumes[seg] = vol
                    material_volumes[seg.material] += vol
                    occupied_volume += vol
        except Exception: continue

    material_volumes["air"] = max(0.0, total_voxel_volume - occupied_volume)
    dominant_material = max(material_volumes, key=material_volumes.get)
    dominant_segment = None

    if dominant_material != "air":
        max_seg_vol = -1.0
        for seg, vol in segment_volumes.items():
            if seg.material == dominant_material:
                if vol > max_seg_vol:
                    max_seg_vol = vol
                    dominant_segment = seg

    # --- HELPER FUNCTIONS ---
    def get_vec(obj, attr):
        val = getattr(obj, attr, None)
        return np.array(val, dtype=float) if val is not None else np.array([0., 0., 0.])

    def safe_float(obj, attr, default_val):
        val = getattr(obj, attr, None)
        return float(val) if val is not None else default_val

    # --- 5. BUILD DIMENSION MATRIX (2x3) ---
    
    # Row 0: Element [r, theta(rad), z]
    row_element = [d_r, d_t, d_z]

    # Row 1: Segment [r, theta(rad), z]
    if dominant_segment is None:
        row_segment = row_element # Air -> Segment = Element
    else:
        # Nếu segment đã có dimension array (từ hàm find_geometry_dimension_in_mesh)
        if hasattr(dominant_segment, 'dimension') and dominant_segment.dimension is not None:
             # dominant_segment.dimension chuẩn là [r, theta, z]
             row_segment = dominant_segment.dimension
        else:
             # Fallback
             seg_r = safe_float(dominant_segment, "r_length", d_r)
             seg_t = safe_float(dominant_segment, "t_length", d_t) 
             seg_z = safe_float(dominant_segment, "z_length", d_z)
             row_segment = [seg_r, seg_t, seg_z]

    dims_array = np.array([
        row_element,
        row_segment
    ], dtype=float)

    # --- 6. RETURN ---
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