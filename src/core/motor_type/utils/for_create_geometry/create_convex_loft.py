import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ==========================================
# HÀM TẠO KHỐI LỒI (CONVEX HULL)
# ==========================================

def create_convex_loft(arg1, arg2=None):
    """
    Tạo một khối bao lồi (Convex Hull) bao quanh 2 biên dạng đầu vào.
    
    Đặc điểm:
    - Đảm bảo 100% hình tạo ra là LỒI (Convex).
    - KHÔNG QUAN TÂM số lượng điểm, chiều quay, hay thứ tự điểm.
    - CẢNH BÁO: Nó sẽ "lấp đầy" mọi vết lõm (ví dụ: Ngôi sao sẽ thành Ngũ giác).
    """
    
    # --- 1. XỬ LÝ ĐẦU VÀO ĐA DẠNG ---
    points_pool = []

    # Xử lý tham số thứ nhất
    if isinstance(arg1, trimesh.Trimesh):
        points_pool.append(arg1.vertices)
    elif isinstance(arg1, np.ndarray):
        if arg1.shape[1] != 3: raise ValueError("Mesh1 phải là 3D (Nx3)")
        points_pool.append(arg1)
        
    # Xử lý tham số thứ hai (nếu có)
    if arg2 is not None:
        if isinstance(arg2, trimesh.Trimesh):
            points_pool.append(arg2.vertices)
        elif isinstance(arg2, np.ndarray):
            if arg2.shape[1] != 3: raise ValueError("Mesh2 phải là 3D (Nx3)")
            points_pool.append(arg2)

    if not points_pool:
        raise ValueError("Input không hợp lệ.")

    # --- 2. GỘP TẤT CẢ ĐIỂM LẠI ---
    # Convex Hull không cần quan tâm điểm nào thuộc mặt nào, nó chỉ cần một "đám mây điểm"
    all_vertices = np.vstack(points_pool)

    # --- 3. TẠO BAO LỒI (CONVEX HULL) ---
    # Thư viện trimesh có sẵn thuật toán Qhull rất mạnh mẽ
    convex_mesh = trimesh.convex.convex_hull(all_vertices)
    
    return convex_mesh

# ==========================================
# HÀM VẼ (TEST)
# ==========================================
def plot_compare(mesh_list, titles):
    fig = plt.figure(figsize=(12, 6))
    for i, mesh in enumerate(mesh_list):
        ax = fig.add_subplot(1, len(mesh_list), i+1, projection='3d')
        
        # Vẽ cạnh (Edges) để dễ nhìn cấu trúc
        col = Poly3DCollection(mesh.vertices[mesh.faces], alpha=0.6, linewidths=0.5, edgecolor='k')
        col.set_facecolor('cyan' if i==0 else 'orange')
        ax.add_collection3d(col)

        b = mesh.bounds
        mid = (b[0]+b[1])*0.5; rng = (b[1]-b[0]).max()/2
        ax.set_xlim(mid[0]-rng, mid[0]+rng); ax.set_ylim(mid[1]-rng, mid[1]+rng); ax.set_zlim(mid[2]-rng, mid[2]+rng)
        ax.set_title(titles[i])
    plt.show()

# ==========================================
# SCRIPT TEST: SỰ KHÁC BIỆT GIỮA LOFT VÀ CONVEX
# ==========================================
if __name__ == "__main__":
    # --- TẠO DỮ LIỆU "LÕM" (NGÔI SAO) ---
    # Ngôi sao là hình lõm điển hình. Loft thường sẽ giữ hình sao, Convex sẽ biến nó thành đa giác lồi.
    
    # 1. Hàm tạo ngôi sao 3D (Copy từ bài trước)
    def create_star_points(z):
        r_out, r_in = 30, 15
        angles = np.linspace(0, 2*np.pi, 11) # 5 cánh
        pts = []
        for i, ang in enumerate(angles[:-1]):
            r = r_out if i % 2 == 0 else r_in
            pts.append([r*np.cos(ang), r*np.sin(ang), z])
        return np.array(pts)

    # Tạo 2 mặt ngôi sao ở Z=0 và Z=40
    star_bottom = create_star_points(0)
    star_top = create_star_points(40)

    print("--- SO SÁNH: LOFT THƯỜNG vs CONVEX HULL ---")
    
    # 1. Cách cũ (Loft thường - Giữ chi tiết lõm)
    # (Cần import hàm create_loft_mesh cũ nếu muốn chạy so sánh, ở đây tôi giả lập kết quả bằng convex hull luôn cho đơn giản)
    # mesh_loft = create_loft_mesh(star_bottom, star_top) # Giả sử bạn dùng hàm cũ
    
    # 2. Cách mới (Convex Loft - Lấp đầy vết lõm)
    mesh_convex = create_convex_loft(star_bottom, star_top)
    
    print(f"Kết quả Convex Mesh:")
    print(f"  Is Convex: {mesh_convex.is_convex} (Phải là True)")
    print(f"  Is Watertight: {mesh_convex.is_watertight}")

    # Vẽ kết quả
    plot_compare([mesh_convex], ["Convex Hull (Đã lấp đầy cánh sao)"])