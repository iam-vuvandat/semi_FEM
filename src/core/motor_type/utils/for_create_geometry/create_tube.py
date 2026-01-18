import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def create_tube(inner_radius, outer_radius, height, z_offset=0.0, sections=360):
    """
    Tạo ống rỗng (Mesh) dùng trimesh.
    Lưu ý: Mặc định sections giảm xuống 64 để Matplotlib vẽ mượt hơn.
    """
    if inner_radius >= outer_radius:
        raise ValueError("Bán kính ngoài phải lớn hơn bán kính trong.")

    # 1. Tạo vỏ và lõi
    cylinder_outer = trimesh.creation.cylinder(radius=outer_radius, height=height, sections=sections)
    cylinder_inner = trimesh.creation.cylinder(radius=inner_radius, height=height + 0.1, sections=sections)

    # 2. Phép trừ khối
    mesh = trimesh.boolean.difference([cylinder_outer, cylinder_inner])

    # 3. Dịch chuyển
    matrix = trimesh.transformations.translation_matrix([0, 0, height/2.0 + z_offset])
    mesh.apply_transform(matrix)

    return mesh

def plot_mesh_matplotlib(mesh, title="3D Tube"):
    """
    Hàm hiển thị đối tượng Trimesh bằng Matplotlib
    """
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 1. Trích xuất các đa giác (polygons) từ mesh
    # mesh.faces chứa chỉ số đỉnh, mesh.vertices chứa tọa độ
    # Dòng này lấy tọa độ thực của từng tam giác tạo nên bề mặt
    polygons = mesh.vertices[mesh.faces]

    # 2. Tạo đối tượng 3D Collection cho Matplotlib
    # alpha: độ trong suốt (0.0 - 1.0)
    # linewidths: độ dày đường viền lưới
    mesh_collection = Poly3DCollection(polygons, alpha=0.7, edgecolor='k', linewidths=0.1)
    
    # Tô màu (có thể tùy chỉnh)
    mesh_collection.set_facecolor((0.2, 0.6, 1.0)) # Màu xanh dương nhạt
    ax.add_collection3d(mesh_collection)

    # 3. Tự động căn chỉnh tỷ lệ trục (Auto-scaling)
    # Matplotlib 3D rất dở trong việc tự căn trục, ta phải set giới hạn thủ công
    # dựa trên kích thước thật của vật thể (bounding box)
    min_limits = mesh.bounds[0]
    max_limits = mesh.bounds[1]

    # Tìm khoảng giá trị lớn nhất để khung hình vuông vức
    max_range = (max_limits - min_limits).max() / 2.0
    mid_x = (max_limits[0] + min_limits[0]) * 0.5
    mid_y = (max_limits[1] + min_limits[1]) * 0.5
    mid_z = (max_limits[2] + min_limits[2]) * 0.5

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    # Thêm nhãn
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)

    plt.show()

# --- Chạy thử ---
if __name__ == "__main__":
    # Tạo ống
    # sections=40 là con số hợp lý cho Matplotlib (đủ tròn mà không quá lag)
    try:
        my_tube = create_tube(inner_radius=3, outer_radius=5, height=10, z_offset=2, sections=40)
        
        # Vẽ bằng Matplotlib
        plot_mesh_matplotlib(my_tube, title="Hình trụ rỗng (Matplotlib)")
        
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")