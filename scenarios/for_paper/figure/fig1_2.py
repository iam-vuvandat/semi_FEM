import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# --- THAM SỐ LƯỚI (Y HỆT CỦA BẠN) ---
r_min, r_max = 70.0, 100.0      
n_r = 6                      
theta_start, theta_end = 0, 270 * np.pi / 180 
n_theta = 36      
z_start, z_end = 0, 60         
n_z = 5                        

alpha_face = 0.1               # Giảm alpha để nhìn xuyên thấu mạch từ bên trong
edge_color = (0, 0, 0, 0.2)    
edge_width = 0.4
start_color = np.array([0.75, 0.88, 1.0]) 
end_color = np.array([1.0, 1.0, 1.0])   

# --- THAM SỐ LINH KIỆN MẠCH TỪ (MRN) ---
node_rad = 0.4
rel_rad = 0.3
mmf_rad = 0.6
color_node = '#1A1A1A'
color_mmf = '#D62728'
color_reluctance = '#FF7F0E'
color_branch = '#888888'

# --- KHỞI TẠO ---
R = np.linspace(r_min, r_max, n_r)
Theta = np.linspace(theta_start, theta_end, n_theta)
Z = np.linspace(z_start, z_end, n_z)

fig = plt.figure(figsize=(12, 12))
ax = fig.add_subplot(111, projection='3d')

# --- HÀM VẼ LINH KIỆN TỐI ƯU ---
def draw_solid_sphere(ax, center, radius, color):
    u, v = np.mgrid[0:2*np.pi:10j, 0:np.pi:10j] # Giảm resolution để tăng tốc
    x = center[0] + radius * np.cos(u) * np.sin(v)
    y = center[1] + radius * np.sin(u) * np.sin(v)
    z = center[2] + radius * np.cos(v)
    ax.plot_surface(x, y, z, color=color, alpha=1.0, linewidth=0, shade=True)

def draw_solid_cylinder(ax, start, end, radius, color):
    v = end - start
    mag = np.linalg.norm(v)
    if mag <= 0: return
    v_unit = v / mag
    not_v = np.array([1, 0, 0]) if (abs(v_unit[0]) < 0.9) else np.array([0, 1, 0])
    n1 = np.cross(v_unit, not_v)
    n1 /= np.linalg.norm(n1)
    n2 = np.cross(v_unit, n1)
    t = np.linspace(0, mag, 2)
    theta = np.linspace(0, 2 * np.pi, 10)
    t, theta = np.meshgrid(t, theta)
    X, Y, Z = [start[i] + v_unit[i] * t + radius * np.sin(theta) * n1[i] + radius * np.cos(theta) * n2[i] for i in [0, 1, 2]]
    ax.plot_surface(X, Y, Z, color=color, alpha=1.0, linewidth=0, shade=True)

all_faces = []
face_colors = []

# --- XỬ LÝ HÌNH HỌC & MẠCH TỪ ---
for i in range(len(R) - 1):
    t_color = i / (len(R) - 2) if len(R) > 2 else 0
    current_color = start_color + (end_color - start_color) * t_color
    
    for j in range(len(Theta) - 1):
        for k in range(len(Z) - 1):
            # 1. Tọa độ đỉnh Voxel (Y hệt lưới của bạn)
            r_v, t_v, z_v = [R[i], R[i+1]], [Theta[j], Theta[j+1]], [Z[k], Z[k+1]]
            v = np.array([
                [r_v[0] * np.cos(t_v[0]), r_v[0] * np.sin(t_v[0]), z_v[0]],
                [r_v[0] * np.cos(t_v[1]), r_v[0] * np.sin(t_v[1]), z_v[0]],
                [r_v[1] * np.cos(t_v[1]), r_v[1] * np.sin(t_v[1]), z_v[0]],
                [r_v[1] * np.cos(t_v[0]), r_v[1] * np.sin(t_v[0]), z_v[0]],
                [r_v[0] * np.cos(t_v[0]), r_v[0] * np.sin(t_v[0]), z_v[1]],
                [r_v[0] * np.cos(t_v[1]), r_v[0] * np.sin(t_v[1]), z_v[1]],
                [r_v[1] * np.cos(t_v[1]), r_v[1] * np.sin(t_v[1]), z_v[1]],
                [r_v[1] * np.cos(t_v[0]), r_v[1] * np.sin(t_v[0]), z_v[1]]
            ])
            faces = [[v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]], 
                     [v[0], v[1], v[5], v[4]], [v[1], v[2], v[6], v[5]], 
                     [v[2], v[3], v[7], v[6]], [v[3], v[0], v[4], v[7]]]
            all_faces.extend(faces)
            face_colors.extend([current_color] * 6)

            # 2. Vẽ mạch từ bên trong mỗi phần tử
            center_node = np.mean(v, axis=0)
            draw_solid_sphere(ax, center_node, node_rad, color_node)

            # 6 mặt của voxel để làm điểm kết nối
            face_centers = [
                np.mean(v[[0,1,5,4]], axis=0), np.mean(v[[2,3,7,6]], axis=0), # R
                np.mean(v[[0,3,7,4]], axis=0), np.mean(v[[1,2,6,5]], axis=0), # Theta
                np.mean(v[[0,1,2,3]], axis=0), np.mean(v[[4,5,6,7]], axis=0)  # Z
            ]

            for f_center in face_centers:
                vec_full = f_center - center_node
                L = np.linalg.norm(vec_full)
                u = vec_full / L
                
                # Vị trí linh kiện (Nối tiếp, không chồng lấn)
                p_rel_start = center_node + u * (L * 0.2)
                p_rel_end   = center_node + u * (L * 0.5)
                p_mmf_center = center_node + u * (L * 0.8)

                # Vẽ khối đặc
                draw_solid_cylinder(ax, p_rel_start, p_rel_end, rel_rad, color_reluctance)
                draw_solid_sphere(ax, p_mmf_center, mmf_rad, color_mmf)

                # Vẽ các đoạn nhánh mảnh (Chỉ vẽ phần hở)
                draw_solid_cylinder(ax, center_node + u * node_rad, p_rel_start, 0.05, color_branch)
                draw_solid_cylinder(ax, p_rel_end, p_mmf_center - u * mmf_rad, 0.05, color_branch)
                draw_solid_cylinder(ax, p_mmf_center + u * mmf_rad, f_center, 0.05, color_branch)

# Vẽ vỏ lưới voxel (Tối ưu hiệu năng của bạn)
poly3d = Poly3DCollection(all_faces, facecolors=face_colors, 
                          alpha=alpha_face, edgecolors=edge_color, linewidths=edge_width)
ax.add_collection3d(poly3d)

# THIẾT LẬP HIỂN THỊ (Y HỆT CỦA BẠN)
ax.set_axis_off() 
limit = r_max
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_zlim(z_start, z_end)
ax.set_box_aspect((2*limit, 2*limit, z_end-z_start))
ax.view_init(elev=31.14, azim=-138.03) # Góc nhìn bạn đã chọn

plt.tight_layout()
plt.show()