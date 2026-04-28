import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# --- THAM SỐ ĐIỀU CHỈNH ---
r_min, r_max = 60.0, 150     
n_r = 6                      

theta_start, theta_end = 0, 100 * np.pi / 180 
n_theta = 36      

z_start, z_end = 0, 60         
n_z = 5                        

alpha_face = 0.85              
edge_color = (0, 0, 0, 0.4)    # Giảm nhẹ độ đậm của viền để hài hòa với màu nhạt
edge_width = 0.6

# Điều chỉnh dải màu: Nhạt và thanh thoát hơn
# start_color là vùng gần tâm (đậm nhất): Màu xanh cực nhẹ
start_color = np.array([0.75, 0.88, 1.0]) 
# end_color là vùng xa tâm (nhạt nhất): Trắng tinh khôi
end_color = np.array([1.0, 1.0, 1.0])   

# --- KHỞI TẠO TỌA ĐỘ ---
R = np.linspace(r_min, r_max, n_r)
Theta = np.linspace(theta_start, theta_end, n_theta)
Z = np.linspace(z_start, z_end, n_z)

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

all_faces = []
face_colors = []

# --- HÀM LẤY GÓC NHÌN TỰ ĐỘNG ---
def on_release(event):
    elev = ax.elev
    azim = ax.azim
    print(f"Góc nhìn hiện tại: ax.view_init(elev={elev:.2f}, azim={azim:.2f})")

# Kết nối sự kiện thả chuột
fig.canvas.mpl_connect('button_release_event', on_release)

# --- XỬ LÝ HÌNH HỌC ---
for i in range(len(R) - 1):
    # Nội suy màu sắc từ xanh nhạt sang trắng theo lớp bán kính
    t = i / (len(R) - 2) if len(R) > 2 else 0
    current_color = start_color + (end_color - start_color) * t
    
    for j in range(len(Theta) - 1):
        for k in range(len(Z) - 1):
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

            faces = [
                [v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]], 
                [v[0], v[1], v[5], v[4]], [v[1], v[2], v[6], v[5]], 
                [v[2], v[3], v[7], v[6]], [v[3], v[0], v[4], v[7]]  
            ]
            
            all_faces.extend(faces)
            face_colors.extend([current_color] * 6)

# Vẽ tập trung để tối ưu hiệu năng
poly3d = Poly3DCollection(all_faces, facecolors=face_colors, 
                          alpha=alpha_face, edgecolors=edge_color, linewidths=edge_width)
ax.add_collection3d(poly3d)

# Loại bỏ các trục tọa độ rác
ax.set_axis_off() 

limit = r_max
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_zlim(z_start, z_end)
ax.set_box_aspect((2*limit, 2*limit, z_end-z_start))

# Góc nhìn bạn đã chọn
ax.view_init(elev=31.14, azim=-138.03)

plt.tight_layout()
plt.show()