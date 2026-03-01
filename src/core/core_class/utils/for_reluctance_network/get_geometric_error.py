import numpy as np
import trimesh
from tqdm import tqdm

def get_geometric_error(reluctance_network):
    object_geometry = reluctance_network.geometry
    geometry_list = object_geometry.geometry

    original_solid_volume = 0.0
    for segment in geometry_list:
        if segment.material == "air":
            pass
        else:
            original_solid_volume += segment.volume

    total_vollume_error = 0.0
    elements_list = reluctance_network.elements.flatten()

    # tqdm hiển thị tiến trình dạng text, không có thanh bar [###---]
    # desc giúp bạn biết hàm đang chạy đến đâu
    progress_bar = tqdm(
        elements_list, 
        bar_format='{desc}: {n_fmt}/{total_fmt} phần tử đã xử lý | Thời gian: {elapsed}', 
        desc='Đang tính toán sai số hình học semiFEM 3D'
    )

    for element in progress_bar:
        # --- 1. TÁI CẤU TRÚC VOXEL TỪ ELEMENT INFO ---
        coord = element.coordinate
        r_avg = (coord[0, 0] + coord[1, 0]) / 2.0
        t_avg = (coord[0, 1] + coord[1, 1]) / 2.0
        z_avg = (coord[0, 2] + coord[1, 2]) / 2.0
        
        d_r = element.dimension[0, 0]
        d_t = element.dimension[0, 1] # Radian
        d_z = element.dimension[0, 2]
        
        grid_arc_len = r_avg * d_t
        
        center_x = r_avg * np.cos(t_avg)
        center_y = r_avg * np.sin(t_avg)
        center_z = z_avg

        voxel_dims = [d_r, grid_arc_len, d_z]
        voxel_mesh = trimesh.creation.box(extents=voxel_dims)

        rotation_matrix = trimesh.transformations.rotation_matrix(t_avg, [0, 0, 1])
        translation_matrix = trimesh.transformations.translation_matrix([center_x, center_y, center_z])
        final_transform = trimesh.transformations.concatenate_matrices(translation_matrix, rotation_matrix)
        voxel_mesh.apply_transform(final_transform)
        
        total_voxel_volume = voxel_mesh.volume
        vox_bounds = voxel_mesh.bounds 

        # --- 2. TÍNH TOÁN THỂ TÍCH CAD CHIẾM CHỖ TRONG Ô LƯỚI ---
        occupied_volume = 0.0
        for seg in geometry_list:
            seg_bounds = seg.mesh.bounds
            
            # Kiểm tra Bounding Box để lọc nhanh
            if not (np.all(vox_bounds[1] > seg_bounds[0]) and np.all(vox_bounds[0] < seg_bounds[1])):
                continue
                
            # Phép toán Boolean có thể gây lỗi nếu mesh CAD không kín (non-manifold)
            # Tôi để mặc định nếu trimesh lỗi nó sẽ văng ra để bạn debug đúng như yêu cầu
            intersection = trimesh.boolean.intersection([voxel_mesh, seg.mesh])
            if intersection.is_volume:
                vol = intersection.volume
                if vol > 1e-12:
                    occupied_volume += vol

        # --- 3. ÁP DỤNG LOGIC SAI SỐ TIÊU CHUẨN VÀNG ---
        if element.material == "air":
            total_vollume_error += float(occupied_volume)
        else:
            total_vollume_error += float(abs(total_voxel_volume - occupied_volume))

    # --- 4. XỬ LÝ ĐỐI XỨNG VÀ TRẢ VỀ ---
    if reluctance_network.mesh.periodic_boundary is True:
        total_vollume_error *= reluctance_network.mechanical.symmetry_factor

    return total_vollume_error / original_solid_volume