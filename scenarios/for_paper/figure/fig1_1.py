import numpy as np
import pyvista as pv

# --- THAM SỐ ĐIỀU CHỈNH ---
r_min, r_max = 48.0, 95.0
n_r = 8

theta_start, theta_end = 0, 100 * np.pi / 180
n_theta = 8

z_start, z_end = 0, 60
n_z = 5

# Màu sắc phong cách khoa học: Xanh nhạt thanh thoát -> Trắng
color_start = "#7FB3D5"  
color_end = "#FFFFFF"    

# --- KHỞI TẠO TỌA ĐỘ ---
R = np.linspace(r_min, r_max, n_r)
Theta = np.linspace(theta_start, theta_end, n_theta)
Z = np.linspace(z_start, z_end, n_z)

points = []
cells = []
cell_types = []
cell_data_radius = []

node_idx = 0
for i in range(len(R) - 1):
    for j in range(len(Theta) - 1):
        for k in range(len(Z) - 1):
            r_v = [R[i], R[i+1]]
            t_v = [Theta[j], Theta[j+1]]
            z_v = [Z[k], Z[k+1]]

            # Tọa độ 8 đỉnh của phần tử MBGRN 3D
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
            
            points.extend(v)
            cell = [8, node_idx, node_idx+1, node_idx+2, node_idx+3, 
                       node_idx+4, node_idx+5, node_idx+6, node_idx+7]
            cells.extend(cell)
            cell_types.append(pv.CellType.HEXAHEDRON)
            cell_data_radius.append(i)
            node_idx += 8

grid = pv.UnstructuredGrid(cells, cell_types, points)
grid.cell_data['RadiusIndex'] = cell_data_radius

# --- THIẾT LẬP HIỂN THỊ PHONG CÁCH KHOA HỌC ---
plotter = pv.Plotter(window_size=[1000, 1000])
plotter.set_background("white")
plotter.enable_anti_aliasing() 

# add_mesh với các thiết lập tối giản
plotter.add_mesh(
    grid, 
    scalars='RadiusIndex',
    cmap=[color_start, color_end],
    show_edges=True, 
    edge_color="black", 
    line_width=1.5,      
    opacity=1.0,         # Không trong suốt để giống Matplotlib nhất
    show_scalar_bar=False,
    lighting=False       # Tắt lighting để màu sắc phẳng và sạch
)

# Chụp góc nhìn camera
def save_cam():
    print(f"\nplotter.camera_position = {plotter.camera_position}")

plotter.add_key_event("c", save_cam)

# Góc nhìn tiêu chuẩn
plotter.camera_position = [
    (245.82, -180.45, 175.21), 
    (22.15, 36.40, 30.00), 
    (-0.38, 0.25, 0.89)
]

plotter.show()