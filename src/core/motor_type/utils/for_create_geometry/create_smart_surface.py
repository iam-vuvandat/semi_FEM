import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# --- HÀM PHỤ: NỘI SUY (RESAMPLING) ---
def resample_path_2d(path, target_count):
    """
    Chia lại các điểm trên đường cong 2D để có đúng target_count điểm.
    Các điểm sẽ phân bố đều theo chiều dài đường cong.
    """
    if len(path) == target_count:
        return path

    # 1. Tính khoảng cách giữa các điểm liên tiếp
    # np.diff tạo mảng vector [p1-p0, p2-p1, ...]
    diffs = np.diff(path, axis=0)
    # Tính độ dài từng đoạn
    dists = np.sqrt(np.sum(diffs**2, axis=1))
    
    # 2. Tính khoảng cách cộng dồn (Cumulative Distance)
    # Thêm 0 vào đầu (khoảng cách tại điểm bắt đầu là 0)
    cum_dist = np.concatenate(([0], np.cumsum(dists)))
    total_length = cum_dist[-1]

    # 3. Tạo các mốc khoảng cách mới đều nhau
    # linspace tạo ra target_count điểm từ 0 đến total_length
    new_dists = np.linspace(0, total_length, target_count)

    # 4. Nội suy tọa độ X và Y theo khoảng cách mới
    new_x = np.interp(new_dists, cum_dist, path[:, 0])
    new_y = np.interp(new_dists, cum_dist, path[:, 1])

    return np.column_stack((new_x, new_y))

# --- 1. HÀM TẠO MESH (ĐÃ NÂNG CẤP) ---
def create_smart_surface(arc1, arc2, z1=0.0, z2=0.0):
    """
    Tạo mesh nối 2 cung tròn 2D. 
    TỰ ĐỘNG XỬ LÝ:
    1. Ngược chiều (Smart Direction).
    2. Lệch số điểm (Auto Resampling).
    """
    # Chuẩn hóa dữ liệu
    arc1 = np.array(arc1, dtype=np.float64)
    arc2 = np.array(arc2, dtype=np.float64)

    if arc1.shape[1] != 2 or arc2.shape[1] != 2:
        raise ValueError("Lỗi: Dữ liệu đầu vào phải là 2D (chỉ có x, y).")
    
    # --- XỬ LÝ SỐ ĐIỂM KHÁC NHAU ---
    n1 = len(arc1)
    n2 = len(arc2)
    
    if n1 != n2:
        # Chọn số điểm mục tiêu. 
        # min() -> giảm điểm để lưới mượt. 
        # max() -> tăng điểm để giữ chi tiết.
        target = min(n1, n2) 
        print(f">> [INFO] Số điểm lệch nhau ({n1} vs {n2}). Đang nội suy về {target} điểm...")
        
        arc1 = resample_path_2d(arc1, target)
        arc2 = resample_path_2d(arc2, target)

    # Cập nhật lại n sau khi resample
    n = len(arc1)

    # --- XỬ LÝ CHIỀU (SMART DIRECTION) ---
    start1, end1 = arc1[0], arc1[-1]
    start2, end2 = arc2[0], arc2[-1]

    dist_direct = np.sum((start1 - start2)**2) + np.sum((end1 - end2)**2)
    dist_cross  = np.sum((start1 - end2)**2) + np.sum((end1 - start2)**2)

    if dist_cross < dist_direct:
        print(">> [INFO] Phát hiện ngược chiều. Đang đảo ngược Arc 2...")
        arc2 = arc2[::-1]

    # --- NÂNG LÊN 3D ---
    z1_arr = np.full(n, z1)
    z2_arr = np.full(n, z2)

    vertices_1 = np.column_stack((arc1, z1_arr))
    vertices_2 = np.column_stack((arc2, z2_arr))

    # --- TẠO MESH ---
    vertices = np.vstack((vertices_1, vertices_2))
    faces = []
    
    for i in range(n - 1):
        idx_1_curr = i
        idx_1_next = i + 1
        idx_2_curr = i + n
        idx_2_next = i + n + 1
        
        faces.append([idx_1_curr, idx_2_curr, idx_1_next])
        faces.append([idx_1_next, idx_2_curr, idx_2_next])

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    return mesh

# --- 2. HÀM VẼ (GIỮ NGUYÊN) ---
def plot_mesh_matplotlib(mesh, title="3D Mesh Plot"):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    polygons = mesh.vertices[mesh.faces]

    mesh_collection = Poly3DCollection(polygons, alpha=0.6, linewidths=0.5, edgecolor='k')
    mesh_collection.set_facecolor((0.2, 0.6, 1.0)) 
    ax.add_collection3d(mesh_collection)

    min_limits = mesh.bounds[0]
    max_limits = mesh.bounds[1]
    mid = (max_limits + min_limits) * 0.5
    max_range = (max_limits - min_limits).max() / 2.0

    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)
    
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
    plt.title(title)
    plt.show()

# --- 3. CHẠY THỬ (TEST CASE LỆCH ĐIỂM) ---
if __name__ == "__main__":
    # Case khó: Số điểm lệch nhau RẤT LỚN
    
    # Đường cong 1: Rất mịn (100 điểm)
    t1 = np.linspace(0, np.pi, 100)
    curve_a = np.column_stack((10*np.cos(t1), 10*np.sin(t1)))
    
    # Đường cong 2: Rất thô (Chỉ 10 điểm)
    t2 = np.linspace(0, np.pi, 10)
    curve_b = np.column_stack((15*np.cos(t2), 15*np.sin(t2)))

    print(f"Input: Curve A ({len(curve_a)} điểm) vs Curve B ({len(curve_b)} điểm)")
    
    try:
        # Gọi hàm
        result_mesh = create_smart_surface(curve_a, curve_b, z1=0.0, z2=20.0)
        
        print("Đang vẽ đồ thị...")
        plot_mesh_matplotlib(result_mesh, title="Mesh từ 2 đường cong khác số điểm")
    except Exception as e:
        print(f"Lỗi: {e}")