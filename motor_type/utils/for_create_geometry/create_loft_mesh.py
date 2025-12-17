import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon

# ==========================================
# 1. CÁC HÀM PHỤ TRỢ (CORE LOGIC)
# ==========================================

def resample_path_3d(path, target_count):
    """
    Nội suy lại đường cong 3D để có đúng số lượng điểm target_count.
    Phân bố điểm đều dựa trên chiều dài cung.
    """
    if len(path) == target_count: return path

    # Tính khoảng cách giữa các điểm
    dists = np.sqrt(np.sum(np.diff(path, axis=0)**2, axis=1))
    cum_dist = np.concatenate(([0], np.cumsum(dists)))
    total_len = cum_dist[-1]

    # Tạo các mốc mới
    new_dists = np.linspace(0, total_len, target_count)

    # Nội suy XYZ
    new_x = np.interp(new_dists, cum_dist, path[:, 0])
    new_y = np.interp(new_dists, cum_dist, path[:, 1])
    new_z = np.interp(new_dists, cum_dist, path[:, 2])

    return np.column_stack((new_x, new_y, new_z))

def align_polygons_3d(p1, p2):
    """
    Xoay vòng và đảo chiều p2 để khớp nhất với p1.
    """
    # Dùng hình chiếu 2D để so sánh cho đơn giản
    p1_xy = p1[:, :2]
    p2_xy = p2[:, :2]
    
    # 1. Căn chỉnh điểm đầu (Start Point)
    pt0 = p1_xy[0]
    dists = np.linalg.norm(p2_xy - pt0, axis=1)
    best_start_idx = np.argmin(dists)
    
    p2_aligned = np.roll(p2, -best_start_idx, axis=0)
    p2_xy_aligned = np.roll(p2_xy, -best_start_idx, axis=0)
    
    # 2. Kiểm tra chiều (Direction)
    pt1 = p1_xy[1]
    dist_forward = np.linalg.norm(p2_xy_aligned[1] - pt1)
    dist_backward = np.linalg.norm(p2_xy_aligned[-1] - pt1)
    
    if dist_backward < dist_forward:
        print(">> [AUTO-FIX] Phát hiện mặt bị ngược chiều. Đang đảo chiều...")
        # Đảo ngược nhưng giữ nguyên điểm đầu để không mất alignment
        p2_rest = p2_aligned[1:][::-1]
        p2_aligned = np.vstack(([p2_aligned[0]], p2_rest))
        
    return p2_aligned

def create_cap_robust(poly_3d, invert_normal=False):
    """Tạo nắp từ biên dạng 3D."""
    try:
        # Triangulate trên 2D
        poly_2d = poly_3d[:, :2]
        z_mean = np.mean(poly_3d[:, 2])
        
        obj = trimesh.creation.triangulate_polygon(Polygon(poly_2d))
        
        if isinstance(obj, tuple):
            cap_mesh = trimesh.Trimesh(vertices=obj[0], faces=obj[1], process=True)
        else:
            cap_mesh = obj

        # Khôi phục độ cao Z
        current_v = cap_mesh.vertices
        cap_mesh.vertices = np.column_stack((current_v[:, 0], current_v[:, 1], np.full(len(current_v), z_mean)))
        
        if invert_normal: cap_mesh.invert()
        return cap_mesh
    except:
        return None

# ==========================================
# 2. HÀM CHÍNH: LOFT BETWEEN MESHES
# ==========================================

def create_loft_mesh(mesh1, mesh2):
    """
    Khâu 2 mặt phẳng (Trimesh objects) thành một khối lồi kín.
    
    Tính năng:
    - Chấp nhận 2 mesh đầu vào với số điểm khác nhau.
    - Tự động xử lý nếu 2 mesh xoay ngược chiều nhau.
    - Trả về khối đặc (Solid Watertight Mesh).
    """
    # 1. Kiểm tra đầu vào
    if not isinstance(mesh1, trimesh.Trimesh) or not isinstance(mesh2, trimesh.Trimesh):
        raise TypeError("Input phải là đối tượng trimesh.Trimesh")

    # 2. Trích xuất đường biên (Vertices)
    # Lưu ý: Ta giả định vertices của mesh đầu vào đã được sắp xếp theo thứ tự vòng lặp.
    # (Điều này đúng nếu mesh được tạo từ các hàm create_surface/polygon trước đó)
    poly1 = mesh1.vertices.copy()
    poly2 = mesh2.vertices.copy()

    # 3. Xử lý số lượng điểm (Resampling)
    n1 = len(poly1)
    n2 = len(poly2)
    
    if n1 != n2:
        # Đưa về số lượng điểm nhỏ hơn để lưới đẹp
        target = min(n1, n2)
        print(f">> [AUTO-FIX] Chênh lệch điểm ({n1} vs {n2}). Nội suy về {target} điểm.")
        if n1 != target: poly1 = resample_path_3d(poly1, target)
        if n2 != target: poly2 = resample_path_3d(poly2, target)
    
    n = len(poly1) # Số điểm thống nhất

    # 4. Căn chỉnh (Alignment)
    # Xoay và đảo chiều poly2 để khớp với poly1
    poly2 = align_polygons_3d(poly1, poly2)

    # 5. Tạo phần Vỏ (Walls) nối 2 biên dạng
    wall_verts = np.vstack((poly1, poly2))
    wall_faces = []
    
    for i in range(n):
        # Nối tam giác (Triangle Strip)
        idx_b_curr = i
        idx_b_next = (i + 1) % n
        idx_t_curr = i + n
        idx_t_next = (i + 1) % n + n
        
        wall_faces.append([idx_b_curr, idx_t_curr, idx_b_next])
        wall_faces.append([idx_b_next, idx_t_curr, idx_t_next])
        
    mesh_walls = trimesh.Trimesh(vertices=wall_verts, faces=wall_faces, process=True)

    # 6. Tạo Nắp (Caps)
    # Chúng ta tạo lại nắp từ poly đã nội suy để đảm bảo khớp khít với vỏ
    cap_1 = create_cap_robust(poly1, invert_normal=True)  # Nắp 1 (Đáy)
    cap_2 = create_cap_robust(poly2, invert_normal=False) # Nắp 2 (Đỉnh)

    # 7. Hợp nhất thành khối đặc
    components = [mesh_walls]
    if cap_1: components.append(cap_1)
    if cap_2: components.append(cap_2)
    
    final_mesh = trimesh.util.concatenate(components)
    final_mesh.merge_vertices()
    
    return final_mesh

# ==========================================
# 3. SCRIPT TEST
# ==========================================
def plot_result(mesh, title):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')
    col = Poly3DCollection(mesh.vertices[mesh.faces], alpha=0.7, linewidths=0.1, edgecolor='k')
    col.set_facecolor('cyan')
    ax.add_collection3d(col)
    
    # Auto-scale view
    b = mesh.bounds
    mid = (b[0]+b[1])*0.5; rng = (b[1]-b[0]).max()/2
    ax.set_xlim(mid[0]-rng, mid[0]+rng)
    ax.set_ylim(mid[1]-rng, mid[1]+rng)
    ax.set_zlim(mid[2]-rng, mid[2]+rng)
    plt.title(title)
    plt.show()

if __name__ == "__main__":
    print("--- TEST: Stitching 2 different Meshes ---")

    # BƯỚC 1: TẠO 2 MESH ĐẦU VÀO KHÁC NHAU (Mô phỏng dữ liệu của bạn)
    
    # Mesh 1: Hình lục giác (6 điểm) ở Z=0
    theta1 = np.linspace(0, 2*np.pi, 6, endpoint=False)
    v1 = np.column_stack((30*np.cos(theta1), 30*np.sin(theta1), np.zeros(6)))
    # Tạo mesh phẳng từ points (giả lập input của bạn)
    f1 = [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 5]] # Triangulation đơn giản
    mesh_input_1 = trimesh.Trimesh(vertices=v1, faces=f1)

    # Mesh 2: Hình tròn (50 điểm) ở Z=40
    # CỐ TÌNH: Xoay ngược chiều và lệch pha
    theta2 = np.linspace(0, 2*np.pi, 50, endpoint=False)
    v2 = np.column_stack((15*np.cos(theta2), 15*np.sin(theta2), np.full(50, 40.0)))
    v2 = v2[::-1] # Đảo ngược chiều
    # Tạo mesh phẳng (không cần faces chuẩn vì ta chỉ lấy vertices)
    mesh_input_2 = trimesh.Trimesh(vertices=v2, faces=[]) 

    print(f"Input 1: {len(mesh_input_1.vertices)} vertices (Hexagon)")
    print(f"Input 2: {len(mesh_input_2.vertices)} vertices (Circle - Reversed)")

    # BƯỚC 2: GỌI HÀM KHÂU
    try:
        solid_mesh = create_loft_mesh(mesh_input_1, mesh_input_2)
        
        print("\n>> KẾT QUẢ:")
        print(f"   Vertices: {len(solid_mesh.vertices)}")
        print(f"   Watertight: {solid_mesh.is_watertight}")
        
        plot_result(solid_mesh, "Stitched Convex Solid")
        
    except Exception as e:
        print(f"Lỗi: {e}")