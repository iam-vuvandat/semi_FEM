import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# --- 1. HÀM XOAY (Giữ nguyên) ---
def rotate_mesh_z(mesh, angle_rad):
    """
    Xoay mesh quanh trục Z (tại chỗ).
    """
    if mesh is None: return
    mesh_returned = mesh.copy()
    matrix = trimesh.transformations.rotation_matrix(angle_rad, [0, 0, 1])
    mesh_returned.apply_transform(matrix)
    return mesh_returned

# --- 2. HÀM VẼ SO SÁNH ---
def plot_comparison(mesh_before, mesh_after, title="Rotation Comparison"):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # --- A. VẼ MESH GỐC (BEFORE) ---
    # Màu xám nhạt, làm nền
    poly_before = mesh_before.vertices[mesh_before.faces]
    col_before = Poly3DCollection(poly_before, alpha=0.3, linewidths=0.5, edgecolor='gray')
    col_before.set_facecolor('lightgray')
    ax.add_collection3d(col_before)

    # --- B. VẼ MESH SAU KHI XOAY (AFTER) ---
    # Màu đỏ nổi bật
    poly_after = mesh_after.vertices[mesh_after.faces]
    col_after = Poly3DCollection(poly_after, alpha=0.8, linewidths=0.5, edgecolor='k')
    col_after.set_facecolor('red')
    ax.add_collection3d(col_after)

    # --- C. VẼ TRỤC TỌA ĐỘ ---
    # Vẽ trục để thấy vật thể quay quanh tâm
    limit = 8
    ax.plot([-limit, limit], [0, 0], [0, 0], 'k--', linewidth=1, label='Axis X')
    ax.plot([0, 0], [-limit, limit], [0, 0], 'k-.', linewidth=1, label='Axis Y')
    ax.plot([0, 0], [0, 0], [-2, 2], 'b-', linewidth=2, label='Axis Z')

    # --- D. CĂN CHỈNH TỈ LỆ ---
    # Lấy bounds lớn nhất để bao trọn cả 2 hình
    # Vì xoay tại chỗ nên bounds không thay đổi nhiều, nhưng cứ tính cho chắc
    all_min = np.minimum(mesh_before.bounds[0], mesh_after.bounds[0])
    all_max = np.maximum(mesh_before.bounds[1], mesh_after.bounds[1])
    
    mid = (all_max + all_min) * 0.5
    max_range = (all_max - all_min).max() / 2.0

    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

    # Legend giả
    import matplotlib.patches as mpatches
    gray_patch = mpatches.Patch(color='lightgray', label='Before (Original)')
    red_patch = mpatches.Patch(color='red', label='After (Rotated 45°)')
    plt.legend(handles=[gray_patch, red_patch])
    
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
    plt.title(title)
    plt.show()

# --- 3. CHẠY TEST ---
if __name__ == "__main__":
    print("--- Test: Xoay thanh dài tại tâm ---")

    # 1. TẠO THANH DÀI (Long Bar)
    # Dài 10 (trục X), Rộng 2 (trục Y), Cao 1 (trục Z)
    # Mặc định tâm tại (0,0,0) -> KHÔNG DỊCH CHUYỂN
    mesh_original = trimesh.creation.box(extents=[10, 2, 1])

    # 2. TẠO BẢN SAO
    mesh_rotated = mesh_original.copy()

    # 3. XOAY 45 ĐỘ
    # Để thấy rõ nó quay chéo đi
    angle = np.radians(45)
    rotate_mesh_z(mesh_rotated, angle)

    print(f"Góc xoay: {np.degrees(angle):.0f} độ")

    # 4. VẼ
    plot_comparison(mesh_original, mesh_rotated, title="Xoay thanh dài tại tâm (Z-Axis)")