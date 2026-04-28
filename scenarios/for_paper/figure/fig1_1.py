import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# --- THAM SỐ HÌNH HỌC ---
r1, r2 = 85.0, 100.0
t1, t2 = np.radians(30), np.radians(60)
z1, z2 = 10.0, 25.0

# --- CẤU HÌNH THẨM MỸ (SOLID COMPONENTS) ---
color_mesh = '#1f77b4'
color_node = '#1A1A1A'         # Nút trung tâm
color_mmf = '#D62728'          # Nguồn MMF
color_reluctance = '#FF7F0E'   # Từ trở
color_branch = '#888888'       # Nhánh dẫn mảnh
alpha_voxel = 0.08

fig_width = 14
fig_height = fig_width / 1.618

fig = plt.figure(figsize=(fig_width, fig_height))
ax = fig.add_subplot(111, projection='3d')

def draw_sphere(ax, center, radius, color):
    u, v = np.mgrid[0:2*np.pi:30j, 0:np.pi:30j]
    x = center[0] + radius * np.cos(u) * np.sin(v)
    y = center[1] + radius * np.sin(u) * np.sin(v)
    z = center[2] + radius * np.cos(v)
    ax.plot_surface(x, y, z, color=color, alpha=1.0, linewidth=0, antialiased=True, shade=True)

def draw_cylinder(ax, start, end, radius, color):
    v = end - start
    mag = np.linalg.norm(v)
    if mag <= 0: return
    v_unit = v / mag
    not_v = np.array([1, 0, 0]) if (abs(v_unit[0]) < 0.9) else np.array([0, 1, 0])
    n1 = np.cross(v_unit, not_v)
    n1 /= np.linalg.norm(n1)
    n2 = np.cross(v_unit, n1)
    t = np.linspace(0, mag, 2)
    theta = np.linspace(0, 2 * np.pi, 25)
    t, theta = np.meshgrid(t, theta)
    X, Y, Z = [start[i] + v_unit[i] * t + radius * np.sin(theta) * n1[i] + radius * np.cos(theta) * n2[i] for i in [0, 1, 2]]
    ax.plot_surface(X, Y, Z, color=color, alpha=1.0, linewidth=0, antialiased=True, shade=True)

# 1. Vẽ Voxel (Vỏ phần tử)
v_pts = np.array([
    [r1 * np.cos(t1), r1 * np.sin(t1), z1], [r1 * np.cos(t2), r1 * np.sin(t2), z1],
    [r2 * np.cos(t2), r2 * np.sin(t2), z1], [r2 * np.cos(t1), r2 * np.sin(t1), z1],
    [r1 * np.cos(t1), r1 * np.sin(t1), z2], [r1 * np.cos(t2), r1 * np.sin(t2), z2],
    [r2 * np.cos(t2), r2 * np.sin(t2), z2], [r2 * np.cos(t1), r2 * np.sin(t1), z2]
])
faces = [[v_pts[0], v_pts[1], v_pts[2], v_pts[3]], [v_pts[4], v_pts[5], v_pts[6], v_pts[7]], 
         [v_pts[0], v_pts[1], v_pts[5], v_pts[4]], [v_pts[2], v_pts[3], v_pts[7], v_pts[6]], 
         [v_pts[1], v_pts[2], v_pts[6], v_pts[5]], [v_pts[4], v_pts[7], v_pts[3], v_pts[0]]]
ax.add_collection3d(Poly3DCollection(faces, alpha=alpha_voxel, facecolors=color_mesh, edgecolors='black', linewidths=0.3))

# 2. Tọa độ nút và các thành phần
center_node = np.mean(v_pts, axis=0)
face_centers = [
    np.mean(v_pts[[0,1,5,4]], axis=0), np.mean(v_pts[[2,3,7,6]], axis=0), 
    np.mean(v_pts[[0,3,7,4]], axis=0), np.mean(v_pts[[1,2,6,5]], axis=0), 
    np.mean(v_pts[[0,1,2,3]], axis=0), np.mean(v_pts[[4,5,6,7]], axis=0)  
]

node_rad = 0.55
mmf_rad = 1.0
rel_rad = 0.45

# 3. Vẽ nút trung tâm
draw_sphere(ax, center_node, radius=node_rad, color=color_node)

# 4. Vẽ các nhánh rời rạc (Không hiển thị phần nằm trong khối đặc)
for f_center in face_centers:
    vec_full = f_center - center_node
    L = np.linalg.norm(vec_full)
    u = vec_full / L
    
    # Xác định các điểm mốc trên nhánh (theo tỉ lệ % chiều dài)
    # Từ trở: 15% đến 45%
    p_rel_start = center_node + u * (L * 0.15)
    p_rel_end   = center_node + u * (L * 0.45)
    
    # Nguồn MMF: Tâm tại 80%
    p_mmf_center = center_node + u * (L * 0.80)
    
    # --- VẼ KHỐI ĐẶC TRƯỚC ---
    draw_cylinder(ax, p_rel_start, p_rel_end, radius=rel_rad, color=color_reluctance)
    draw_sphere(ax, p_mmf_center, radius=mmf_rad, color=color_mmf)
    
    # --- VẼ CÁC ĐOẠN NHÁNH MẢNH (Chỉ vẽ phần hở) ---
    # Đoạn 1: Từ bề mặt nút trung tâm đến đầu Từ trở
    draw_cylinder(ax, center_node + u * node_rad, p_rel_start, radius=0.05, color=color_branch)
    
    # Đoạn 2: Từ cuối Từ trở đến bề mặt nguồn MMF
    draw_cylinder(ax, p_rel_end, p_mmf_center - u * mmf_rad, radius=0.05, color=color_branch)
    
    # Đoạn 3: Từ bề mặt nguồn MMF đến tâm mặt (biên phần tử)
    draw_cylinder(ax, p_mmf_center + u * mmf_rad, f_center, radius=0.05, color=color_branch)

# Thiết lập hiển thị
ax.set_axis_off()
ax.set_box_aspect([1, 1, 0.8])
ax.view_init(elev=22, azim=-52)

plt.tight_layout()
plt.show()