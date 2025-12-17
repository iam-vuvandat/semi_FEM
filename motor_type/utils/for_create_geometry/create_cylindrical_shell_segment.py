import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from shapely.geometry import Polygon

# --- 1. Hàm tạo hình học (Đã đổi sang Radian) ---
def create_cylindrical_shell_segment(inner_radius, outer_radius, height, 
                                     angle_rad,            # Đơn vị: Radian
                                     center_angle_rad=0.0, # Đơn vị: Radian
                                     z_offset=0.0, 
                                     sections=30):
    """
    Tạo phân đoạn vỏ trụ (Nam châm hình cung) sử dụng đơn vị Radian.
    
    Tham số:
    - angle_rad: Góc mở của mảnh (Ví dụ: np.pi/3).
    - center_angle_rad: Góc vị trí trung tâm so với trục X.
    """
    if inner_radius >= outer_radius:
        raise ValueError("Bán kính ngoài phải lớn hơn bán kính trong.")

    # A. Tạo biên dạng 2D
    # Không cần convert np.radians() nữa vì đầu vào đã là radian
    theta_rad = angle_rad 
    
    # Tạo mảng góc từ -theta/2 đến +theta/2
    angles = np.linspace(-theta_rad/2, theta_rad/2, sections)
    
    # Cung trong (Inner)
    x_inner = inner_radius * np.cos(angles)
    y_inner = inner_radius * np.sin(angles)
    inner_points = np.column_stack((x_inner, y_inner))
    
    # Cung ngoài (Outer)
    x_outer = outer_radius * np.cos(angles)
    y_outer = outer_radius * np.sin(angles)
    outer_points = np.column_stack((x_outer, y_outer))
    
    # Kết hợp thành vòng khép kín
    vertices_2d = np.vstack((inner_points, outer_points[::-1]))

    # B. Extrude (Đùn khối)
    poly = Polygon(vertices_2d)
    mesh = trimesh.creation.extrude_polygon(poly, height=height)

    # C. Dịch chuyển và Xoay
    translation_z = z_offset
    mesh.apply_translation([0, 0, translation_z])

    # Xoay về góc mong muốn (Dùng trực tiếp radian)
    if center_angle_rad != 0:
        rot_matrix = trimesh.transformations.rotation_matrix(
            center_angle_rad, # Đã là radian, dùng luôn
            [0, 0, 1]
        )
        mesh.apply_transform(rot_matrix)

    return mesh

# --- 2. Hàm vẽ (Giữ nguyên) ---
def plot_segments_matplotlib(segments, colors=None, title="Arc Magnets"):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    all_min, all_max = [], []

    if not isinstance(segments, list): segments = [segments]

    for i, mesh in enumerate(segments):
        polygons = mesh.vertices[mesh.faces]
        c = colors[i] if colors and i < len(colors) else (0.2, 0.6, 1.0, 0.6)
        
        mesh_collection = Poly3DCollection(polygons, alpha=c[3] if len(c)>3 else 0.8, 
                                           linewidths=0, edgecolor='none')
        mesh_collection.set_facecolor(c[:3])
        ax.add_collection3d(mesh_collection)
        all_min.append(mesh.bounds[0])
        all_max.append(mesh.bounds[1])

    if all_min and all_max:
        global_min = np.min(all_min, axis=0)
        global_max = np.max(all_max, axis=0)
        max_range = (global_max - global_min).max() / 2.0
        mid = (global_max + global_min) * 0.5
        ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
        ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
        ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
    plt.title(title)
    plt.show()

# --- 3. Chạy thử với Radian ---
if __name__ == "__main__":
    # Thông số mảnh mỏng
    R_in = 10.0
    R_out = 40.0
    H = 2.0
    
    # QUAN TRỌNG: Nhập góc bằng Radian
    # Ví dụ: Muốn mở 60 độ -> dùng np.pi / 3
    # Muốn mở 45 độ -> dùng np.pi / 4
    span_rad = np.pi / 3  # ~1.047 radians (60 độ)
    
    print(f"Đang tạo mảnh mỏng với góc mở {span_rad:.4f} rad...")

    seg_thin = create_cylindrical_shell_segment(
        inner_radius=R_in, 
        outer_radius=R_out, 
        height=H, 
        angle_rad=span_rad,          # Truyền radian
        center_angle_rad=0.0,        # Góc 0
        sections=60,
        z_offset= 0
    )
    

    plot_segments_matplotlib(
        [seg_thin], 
        colors=[(0.9, 0.1, 0.1, 0.7), (0.1, 0.9, 0.1, 0.7)], 
        title="Arc Segment (Unit: Radian)"
    )