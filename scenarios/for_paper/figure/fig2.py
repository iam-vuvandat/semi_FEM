import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# --- THAM SỐ ĐIỀU CHỈNH ---
r_min, r_max = 48.0, 95.0      
n_r = 6                       
theta_start, theta_end = 0, 100 * np.pi / 180 
n_theta = 12 
z_start, z_end = 0, 40 
n_z = 5                        

# Cập nhật màu xanh từ fig 1 cho phần tử trung tâm
target_color = np.array([0.75, 0.88, 1.0]) 
other_color = np.array([0.96, 0.96, 0.96]) 

R = np.linspace(r_min, r_max, n_r)
Theta = np.linspace(theta_start, theta_end, n_theta)
Z = np.linspace(z_start, z_end, n_z)

def get_vertices(i, j, k):
    r_v = [R[i], R[i+1]]
    t_v = [Theta[j], Theta[j+1]]
    z_v = [Z[k], Z[k+1]]
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
    return v

def get_faces(v):
    return [
        [v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]], 
        [v[0], v[1], v[5], v[4]], [v[1], v[2], v[6], v[5]], 
        [v[2], v[3], v[7], v[6]], [v[3], v[0], v[4], v[7]]  
    ]

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

i, j, k = 2, 5, 2
target_idx = (i, j, k)
v_center = get_vertices(i, j, k)
center_pt = np.mean(v_center, axis=0)

neighbors = [(i+1, j, k), (i-1, j, k), (i, j+1, k), (i, j-1, k), (i, j, k+1), (i, j, k-1)]

all_points = []

for idx in [target_idx] + neighbors:
    ni, nj, nk = idx
    v_n = get_vertices(ni, nj, nk)
    all_points.extend(v_n)
    n_pt = np.mean(v_n, axis=0)
    
    is_target = (idx == target_idx)
    current_color = target_color if is_target else other_color
    alpha = 0.95 if is_target else 0.4
    
    ax.add_collection3d(Poly3DCollection(get_faces(v_n), facecolors=[current_color]*6, 
                                          alpha=alpha, edgecolors=(0,0,0,0.15), linewidths=0.5))
    
    if not is_target:
        ax.plot([center_pt[0], n_pt[0]], [center_pt[1], n_pt[1]], [center_pt[2], n_pt[2]], 
                'k--', linewidth=1.0, alpha=0.3)
        ax.scatter(n_pt[0], n_pt[1], n_pt[2], color='black', s=6, alpha=0.4)

# Điểm tiềm năng nhỏ tại tâm
ax.scatter(center_pt[0], center_pt[1], center_pt[2], color='red', s=10, zorder=10)

all_points = np.array(all_points)
x_range = all_points[:,0].max() - all_points[:,0].min()
y_range = all_points[:,1].max() - all_points[:,1].min()
z_range = all_points[:,2].max() - all_points[:,2].min()
ax.set_box_aspect((x_range, y_range, z_range))

ax.set_axis_off()
ax.view_init(elev=28, azim=-132)

plt.tight_layout()
plt.show()