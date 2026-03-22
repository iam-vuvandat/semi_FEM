import numpy as np
import matplotlib
# Sử dụng TkAgg để ổn định hơn cho Surface Pro 5
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Tối ưu hóa render chung của Matplotlib
matplotlib.rcParams['path.simplify'] = True
matplotlib.rcParams['path.simplify_threshold'] = 1.0
matplotlib.rcParams['agg.path.chunksize'] = 10000

# --- THAM SỐ ĐIỀU CHỈNH ---
r_min, r_max = 70.0, 100.0      
n_r = 6                       

theta_start, theta_end = 0, 320 * np.pi / 180 
n_theta = 36      

z_start, z_end = 0, 60         
n_z = 5                             

alpha_face = 0.85              
edge_color = (0, 0, 0, 0.6)    
edge_width = 0.5 

start_color = np.array([0.75, 0.88, 1.0]) 
red_pale = np.array([1.0, 0.75, 0.75]) # Màu đỏ nhạt cho CV quay vòng
white_color = np.array([1.0, 1.0, 1.0])   

# --- KHỞI TẠO TỌA ĐỘ ---
R = np.linspace(r_min, r_max, n_r)
Theta = np.linspace(theta_start, theta_end, n_theta)
Z = np.linspace(z_start, z_end, n_z)

delta_theta = Theta[1] - Theta[0]
n_j_max = len(Theta) - 1

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

all_faces = []
face_colors = []

def on_release(event):
    elev = ax.elev
    azim = ax.azim
    print(f"Góc nhìn hiện tại: ax.view_init(elev={elev:.2f}, azim={azim:.2f})")
    fig.canvas.draw_idle()

fig.canvas.mpl_connect('button_release_event', on_release)

# --- XỬ LÝ HÌNH HỌC ---
for i in range(len(R) - 1):
    for j in range(n_j_max):
        for k in range(len(Z) - 1):
            if i < 2:
                s = 2
                # 1. Vẽ CV màu xanh lòi ra ngoài
                current_color = start_color
                r_v = [R[i], R[i+1]]
                t_v = [Theta[j] + s * delta_theta, Theta[j+1] + s * delta_theta]
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
                faces = [[v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]], 
                         [v[0], v[1], v[5], v[4]], [v[1], v[2], v[6], v[5]], 
                         [v[2], v[3], v[7], v[6]], [v[3], v[0], v[4], v[7]]]
                all_faces.extend(faces)
                face_colors.extend([current_color] * 6)

                # 2. Nếu chỉ số j + s vượt quá biên, vẽ thêm CV màu đỏ nhạt quay vòng về đầu
                if (j + s) >= n_j_max:
                    j_wrapped = (j + s) % n_j_max
                    t_v_wrap = [Theta[j_wrapped], Theta[j_wrapped] + delta_theta]
                    
                    v_wrap = np.array([
                        [r_v[0] * np.cos(t_v_wrap[0]), r_v[0] * np.sin(t_v_wrap[0]), z_v[0]],
                        [r_v[0] * np.cos(t_v_wrap[1]), r_v[0] * np.sin(t_v_wrap[1]), z_v[0]],
                        [r_v[1] * np.cos(t_v_wrap[1]), r_v[1] * np.sin(t_v_wrap[1]), z_v[0]],
                        [r_v[1] * np.cos(t_v_wrap[0]), r_v[1] * np.sin(t_v[0]), z_v[0]], # Sửa lại logic index
                        [r_v[0] * np.cos(t_v_wrap[0]), r_v[0] * np.sin(t_v_wrap[0]), z_v[1]],
                        [r_v[0] * np.cos(t_v_wrap[1]), r_v[0] * np.sin(t_v_wrap[1]), z_v[1]],
                        [r_v[1] * np.cos(t_v_wrap[1]), r_v[1] * np.sin(t_v_wrap[1]), z_v[1]],
                        [r_v[1] * np.cos(t_v_wrap[0]), r_v[1] * np.sin(t_v[0]), z_v[1]]
                    ])
                    # Sửa lại v_wrap để đảm bảo hình học chuẩn lăng trụ
                    v_wrap = np.array([
                        [r_v[0] * np.cos(t_v_wrap[0]), r_v[0] * np.sin(t_v_wrap[0]), z_v[0]],
                        [r_v[0] * np.cos(t_v_wrap[1]), r_v[0] * np.sin(t_v_wrap[1]), z_v[0]],
                        [r_v[1] * np.cos(t_v_wrap[1]), r_v[1] * np.sin(t_v_wrap[1]), z_v[0]],
                        [r_v[1] * np.cos(t_v_wrap[0]), r_v[1] * np.sin(t_v_wrap[0]), z_v[0]],
                        [r_v[0] * np.cos(t_v_wrap[0]), r_v[0] * np.sin(t_v_wrap[0]), z_v[1]],
                        [r_v[0] * np.cos(t_v_wrap[1]), r_v[0] * np.sin(t_v_wrap[1]), z_v[1]],
                        [r_v[1] * np.cos(t_v_wrap[1]), r_v[1] * np.sin(t_v_wrap[1]), z_v[1]],
                        [r_v[1] * np.cos(t_v_wrap[0]), r_v[1] * np.sin(t_v_wrap[0]), z_v[1]]
                    ])
                    faces_wrap = [[v_wrap[0], v_wrap[1], v_wrap[2], v_wrap[3]], [v_wrap[4], v_wrap[5], v_wrap[6], v_wrap[7]], 
                                  [v_wrap[0], v_wrap[1], v_wrap[5], v_wrap[4]], [v_wrap[1], v_wrap[2], v_wrap[6], v_wrap[5]], 
                                  [v_wrap[2], v_wrap[3], v_wrap[7], v_wrap[6]], [v_wrap[3], v_wrap[0], v_wrap[4], v_wrap[7]]]
                    all_faces.extend(faces_wrap)
                    face_colors.extend([red_pale] * 6)
            else:
                # Stator đứng yên màu trắng
                s = 0
                current_color = white_color
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
                faces = [[v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]], 
                         [v[0], v[1], v[5], v[4]], [v[1], v[2], v[6], v[5]], 
                         [v[2], v[3], v[7], v[6]], [v[3], v[0], v[4], v[7]]]
                all_faces.extend(faces)
                face_colors.extend([current_color] * 6)

poly3d = Poly3DCollection(all_faces, facecolors=face_colors, 
                          alpha=alpha_face, edgecolors=edge_color, 
                          linewidths=edge_width, antialiased=False)
ax.add_collection3d(poly3d)

ax.set_axis_off() 

limit = r_max * 1.2
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_zlim(z_start, z_end)
ax.set_box_aspect((2*limit, 2*limit, z_end-z_start))

ax.view_init(elev=31.14, azim=-138.03)

plt.tight_layout()
plt.show()