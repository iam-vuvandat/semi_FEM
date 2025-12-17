import numpy as np
import trimesh
from tqdm import tqdm

def find_geometry_dimension_in_mesh(geometry, mesh):
    """
    Đo đạc kích thước [r, theta, z] của các segment trong không gian lưới.
    Cập nhật trực tiếp thuộc tính: seg.dimension = np.array([r, theta, z]).
    
    r: Chiều dày theo phương bán kính.
    theta: Góc mở (Radian).
    z: Chiều dài theo phương trục.
    """
    
    # 1. Lấy danh sách segment
    segments = geometry.geometry if hasattr(geometry, 'geometry') else geometry
    
    # 2. Lấy dữ liệu lưới
    r_nodes = mesh.r_nodes
    t_nodes = mesh.theta_nodes
    z_nodes = mesh.z_nodes
    
    # Xác định phạm vi bao phủ của toàn bộ Grid
    grid_r_min, grid_r_max = r_nodes[0], r_nodes[-1]
    grid_z_min, grid_z_max = z_nodes[0], z_nodes[-1]
    
    print(f"[INFO] Measuring Segments within Mesh Grid...")
    
    count_out_of_bounds = 0
    count_fallback = 0
    
    for seg in tqdm(segments, desc="Processing"):
        # Mặc định reset dimension về [0,0,0] nếu cần, hoặc giữ nguyên
        # Ở đây ta sẽ tính toán giá trị mới
        
        if seg.mesh is None:
            continue
            
        # --- BƯỚC 1: KHOANH VÙNG & CHECK OUT-OF-BOUNDS ---
        # Lấy Bounding Box Descartes
        bbox_min, bbox_max = seg.mesh.bounds
        z_seg_min, z_seg_max = bbox_min[2], bbox_max[2]
        
        # Chuyển đổi BBox sang hệ trụ (ước lượng r)
        corners = trimesh.bounds.corners(seg.mesh.bounds)
        r_corners = np.sqrt(corners[:,0]**2 + corners[:,1]**2)
        r_seg_min, r_seg_max = np.min(r_corners), np.max(r_corners)
        
        # Kiểm tra nhanh: Segment có nằm hoàn toàn ngoài phạm vi R hoặc Z của lưới không?
        if (r_seg_max < grid_r_min or r_seg_min > grid_r_max or 
            z_seg_max < grid_z_min or z_seg_min > grid_z_max):
            
            count_out_of_bounds += 1
            # Segment ngoài vùng tính toán -> Set dimension = 0 hoặc giữ nguyên
            seg.dimension = np.array([0., 0., 0.])
            continue

        # --- BƯỚC 2: TÌM INDEX TRÊN GRID ---
        # Tìm index range (mở rộng biên +/- 1 để an toàn)
        i_r_start = max(0, np.searchsorted(r_nodes, r_seg_min) - 1)
        i_r_end   = min(len(r_nodes)-1, np.searchsorted(r_nodes, r_seg_max) + 1)
        
        i_z_start = max(0, np.searchsorted(z_nodes, z_seg_min) - 1)
        i_z_end   = min(len(z_nodes)-1, np.searchsorted(z_nodes, z_seg_max) + 1)
        
        # Theta quét toàn bộ (để an toàn vì BBox Descartes không phản ánh đúng góc)
        i_t_start, i_t_end = 0, len(t_nodes) - 1
        
        if i_r_start >= i_r_end or i_z_start >= i_z_end:
            count_out_of_bounds += 1
            seg.dimension = np.array([0., 0., 0.])
            continue

        # --- BƯỚC 3: TẠO LƯỚI TÂM CỤC BỘ ---
        r_sub = r_nodes[i_r_start : i_r_end+1]
        t_sub = t_nodes[i_t_start : i_t_end+1]
        z_sub = z_nodes[i_z_start : i_z_end+1]
        
        r_c = (r_sub[:-1] + r_sub[1:]) / 2
        t_c = (t_sub[:-1] + t_sub[1:]) / 2
        z_c = (z_sub[:-1] + z_sub[1:]) / 2
        
        # Meshgrid 3D
        R_g, T_g, Z_g = np.meshgrid(r_c, t_c, z_c, indexing='ij')
        
        # Sang Descartes để check va chạm
        X_flat = (R_g * np.cos(T_g)).flatten()
        Y_flat = (R_g * np.sin(T_g)).flatten()
        Z_flat = Z_g.flatten()
        
        candidates = np.column_stack((X_flat, Y_flat, Z_flat))
        
        if len(candidates) == 0:
            count_out_of_bounds += 1
            continue

        # --- BƯỚC 4: KIỂM TRA VA CHẠM ---
        mask = seg.mesh.contains(candidates)
        
        # Khởi tạo biến kết quả
        r_val, theta_val, z_val = 0.0, 0.0, 0.0

        # --- BƯỚC 5: TÍNH TOÁN KÍCH THƯỚC ---
        if np.any(mask):
            # == TRƯỜNG HỢP 1: CÓ VOXEL BỊ CHIẾM (LÝ TƯỞNG) ==
            mask_3d = mask.reshape(len(r_c), len(t_c), len(z_c))
            valid_r, valid_t, valid_z = np.where(mask_3d)
            
            # A. R Length
            min_r, max_r = np.min(valid_r), np.max(valid_r)
            r_val = float(r_sub[max_r + 1] - r_sub[min_r])
            
            # B. Theta (Góc mở - Radian)
            min_t, max_t = np.min(valid_t), np.max(valid_t)
            # Tính góc mở trực tiếp từ node t
            theta_val = float(t_sub[max_t + 1] - t_sub[min_t])
            
            # C. Z Length
            min_z, max_z = np.min(valid_z), np.max(valid_z)
            z_val = float(z_sub[max_z + 1] - z_sub[min_z])
            
        else:
            # == TRƯỜNG HỢP 2: FALLBACK (SEGMENT QUÁ MỎNG) ==
            # Segment nhỏ hơn 1 ô lưới, dùng BBox hoặc kích thước ô lưới làm fallback
            count_fallback += 1
            
            # Z fallback: Dùng chiều cao BBox
            z_val = float(z_seg_max - z_seg_min)
            
            # R fallback: Dùng bề dày BBox theo phương R
            r_val = float(r_seg_max - r_seg_min)
            
            # Theta fallback:
            # Vì segment quá nhỏ để chiếm 1 voxel, ta không thể đo chính xác góc.
            # Ta lấy kích thước của 1 ô lưới góc (dt) làm kích thước tối thiểu.
            if len(t_sub) > 1:
                 dt_grid = t_sub[1] - t_sub[0]
                 theta_val = float(dt_grid)
            else:
                 theta_val = 0.0 # Should not happen if grid is valid

            # Fallback an toàn nếu BBox = 0 (điểm hoặc đường thẳng)
            if r_val < 1e-9 and len(r_sub) > 1: r_val = float(r_sub[1] - r_sub[0])
            if z_val < 1e-9 and len(z_sub) > 1: z_val = float(z_sub[1] - z_sub[0])

        # --- BƯỚC 6: CẬP NHẬT DIMENSION CHO SEGMENT ---
        seg.dimension = np.array([r_val, theta_val, z_val])

    if count_out_of_bounds > 0:
        print(f"[INFO] Skipped {count_out_of_bounds} segments completely out of mesh bounds.")
    if count_fallback > 0:
        print(f"[WARNING] Used fallback dimension for {count_fallback} segments (Mesh too coarse).")
    
    print("[INFO] Dimensions calculation completed.")