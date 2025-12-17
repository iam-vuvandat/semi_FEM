import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon

# ==========================================
# 1. CÁC HÀM PHỤ TRỢ (HELPER FUNCTIONS)
# ==========================================

def get_coords_from_polygon(poly):
    """Trích xuất mảng (N, 2) từ Shapely Polygon hoặc Numpy Array."""
    if isinstance(poly, Polygon):
        # Lấy tọa độ đường bao ngoài, bỏ điểm cuối (vì trùng điểm đầu)
        return np.array(poly.exterior.coords)[:-1]
    return np.array(poly)

def resample_path_2d(path, target_count):
    """Nội suy đường cong 2D để có đúng target_count điểm."""
    if len(path) == target_count: return path
    
    # Tính chu vi dồn tích
    dists = np.sqrt(np.sum(np.diff(path, axis=0, append=path[:1])**2, axis=1))
    cum_dist = np.concatenate(([0], np.cumsum(dists[:-1]))) # Bỏ đoạn nối cuối về đầu để tính linear
    total_len = cum_dist[-1] + np.linalg.norm(path[-1] - path[0]) # Chu vi khép kín
    
    # Do là vòng kín, ta nội suy theo chu vi vòng tròn
    # (Logic đơn giản hóa: coi như đường hở rồi đóng lại)
    # Để chính xác nhất cho Polygon kín:
    path_closed = np.vstack((path, path[0])) # Đóng vòng
    dists_closed = np.sqrt(np.sum(np.diff(path_closed, axis=0)**2, axis=1))
    cum_dist_closed = np.concatenate(([0], np.cumsum(dists_closed)))
    
    new_dists = np.linspace(0, cum_dist_closed[-1], target_count + 1)[:-1] # Bỏ điểm cuối trùng
    
    new_x = np.interp(new_dists, cum_dist_closed, path_closed[:, 0])
    new_y = np.interp(new_dists, cum_dist_closed, path_closed[:, 1])
    
    return np.column_stack((new_x, new_y))

def align_polygons_2d(p1, p2):
    """Căn chỉnh p2 theo p1 (trên mặt phẳng 2D)."""
    # 1. Căn chỉnh điểm đầu
    pt0 = p1[0]
    dists = np.linalg.norm(p2 - pt0, axis=1)
    best_idx = np.argmin(dists)
    p2_aligned = np.roll(p2, -best_idx, axis=0)
    
    # 2. Kiểm tra chiều (ngược/xuôi)
    pt1 = p1[1]
    dist_fw = np.linalg.norm(p2_aligned[1] - pt1)
    dist_bw = np.linalg.norm(p2_aligned[-1] - pt1)
    
    if dist_bw < dist_fw:
        print(">> [INFO] Phát hiện ngược chiều. Đang đảo chiều Polygon 2...")
        # Đảo chiều giữ nguyên điểm đầu
        p2_rest = p2_aligned[1:][::-1]
        p2_aligned = np.vstack(([p2_aligned[0]], p2_rest))
        
    return p2_aligned

def create_cap_from_points(points_2d, z_height, invert=False):
    """Tạo nắp từ mảng điểm 2D."""
    try:
        poly = Polygon(points_2d)
        obj = trimesh.creation.triangulate_polygon(poly)
        mesh = trimesh.Trimesh(vertices=obj[0], faces=obj[1]) if isinstance(obj, tuple) else obj
        
        # Gán Z
        v = mesh.vertices
        mesh.vertices = np.column_stack((v[:,0], v[:,1], np.full(len(v), z_height)))
        
        if invert: mesh.invert()
        return mesh
    except:
        return None

# ==========================================
# 2. HÀM CHÍNH: CREATE FRUSTUM LOFT
# ==========================================

def create_frustum_loft(poly1, poly2, z1, z2):
    """
    Tạo khối hình cụt (Frustum/Loft) nối giữa 2 Polygon tại 2 độ cao Z.
    
    Tham số:
    - poly1: Polygon đáy (Shapely Polygon hoặc Array Nx2).
    - poly2: Polygon đỉnh (Shapely Polygon hoặc Array Nx2).
    - z1: Độ cao đáy.
    - z2: Độ cao đỉnh.
    """
    # 1. Chuẩn hóa đầu vào thành Array (N, 2)
    pts1 = get_coords_from_polygon(poly1)
    pts2 = get_coords_from_polygon(poly2)

    # 2. Resampling (Đồng bộ số điểm)
    n1, n2 = len(pts1), len(pts2)
    target = max(n1, n2) # Lấy số lớn hơn để giữ chi tiết
    
    if n1 != target: pts1 = resample_path_2d(pts1, target)
    if n2 != target: pts2 = resample_path_2d(pts2, target)
    
    n = len(pts1)

    # 3. Alignment (Căn chỉnh)
    pts2 = align_polygons_2d(pts1, pts2)

    # 4. Nâng lên 3D (Thêm tọa độ Z)
    verts1 = np.column_stack((pts1, np.full(n, z1)))
    verts2 = np.column_stack((pts2, np.full(n, z2)))

    # 5. Tạo Vỏ (Walls)
    wall_verts = np.vstack((verts1, verts2))
    wall_faces = []
    for i in range(n):
        # Triangle Strip khép kín
        curr = i
        next_ = (i + 1) % n
        curr_top = i + n
        next_top = (i + 1) % n + n
        
        # Tam giác 1
        wall_faces.append([curr, curr_top, next_])
        # Tam giác 2
        wall_faces.append([next_, curr_top, next_top])
        
    mesh_walls = trimesh.Trimesh(vertices=wall_verts, faces=wall_faces, process=True)

    # 6. Tạo Nắp (Caps)
    cap_bottom = create_cap_from_points(pts1, z1, invert=True)
    cap_top = create_cap_from_points(pts2, z2, invert=False)

    # 7. Gộp lại
    components = [mesh_walls]
    if cap_bottom: components.append(cap_bottom)
    if cap_top: components.append(cap_top)
    
    final_mesh = trimesh.util.concatenate(components)
    final_mesh.merge_vertices()
    
    return final_mesh

# ==========================================
# 3. SCRIPT TEST
# ==========================================
if __name__ == "__main__":
    def plot_result(mesh, title):
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        col = Poly3DCollection(mesh.vertices[mesh.faces], alpha=0.8, linewidths=0.1, edgecolor='k')
        col.set_facecolor('orange')
        ax.add_collection3d(col)
        b = mesh.bounds; mid = (b[0]+b[1])*0.5; rng = (b[1]-b[0]).max()/2
        ax.set_xlim(mid[0]-rng, mid[0]+rng); ax.set_ylim(mid[1]-rng, mid[1]+rng); ax.set_zlim(mid[2]-rng, mid[2]+rng)
        plt.title(title); plt.show()

    print("--- TEST: Hình Chóp Cụt (Hình vuông -> Hình tròn) ---")
    
    # Đáy: Hình vuông (Shapely Polygon)
    sq = Polygon([(-30,-30), (30,-30), (30,30), (-30,30)])
    
    # Đỉnh: Hình tròn (Numpy Array - Ít điểm)
    theta = np.linspace(0, 2*np.pi, 20, endpoint=False)
    circ = np.column_stack((15*np.cos(theta), 15*np.sin(theta)))
    
    # Gọi hàm (Square Z=0 -> Circle Z=50)
    try:
        frustum = create_frustum_loft(sq, circ, z1=0, z2=50)
        
        print(f"Mesh Created! V: {len(frustum.vertices)}, F: {len(frustum.faces)}")
        print(f"Watertight: {frustum.is_watertight}")
        plot_result(frustum, "Square to Circle Frustum")
        
    except Exception as e:
        print(f"Lỗi: {e}")