import trimesh
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import sys

# ==============================================================================
# CONFIGURATION - CÁC THÔNG SỐ ĐIỀU CHỈNH
# ==============================================================================
SHOW_ORIGINAL = False       
SHOW_GRID = False              

EXTENTS = (0.8, 0.8, 0.4)      
#EXTENTS = (0.8, 0.8, 0.2)      
CENTER_OFFSET = (1.0, 1.0, 0) 

COLOR_A = "#C0E0FE"           
OPACITY_A = 1.0                

R_LIMITS = (0.6, 2.2)          
THETA_LIMITS = ( 20 * (np.pi / 180)    ,  70    * (np.pi / 180)) 
Z_LIMITS = (-0.07, 0.07)         

N_R = 60              
N_THETA = 60    
N_Z = 10            

GRID_COLOR = "black"
GRID_OPACITY = 0.1
LINE_WIDTH_CV = 0.5
# ==============================================================================

def get_cv_vertices(rv, tv, zv):
    v = np.array([
        [rv[0]*np.cos(tv[0]), rv[0]*np.sin(tv[0]), zv[0]],
        [rv[0]*np.cos(tv[1]), rv[0]*np.sin(tv[1]), zv[0]],
        [rv[1]*np.cos(tv[1]), rv[1]*np.sin(tv[1]), zv[0]],
        [rv[1]*np.cos(tv[0]), rv[1]*np.sin(tv[0]), zv[0]],
        [rv[0]*np.cos(tv[0]), rv[0]*np.sin(tv[0]), zv[1]],
        [rv[0]*np.cos(tv[1]), rv[0]*np.sin(tv[1]), zv[1]],
        [rv[1]*np.cos(tv[1]), rv[1]*np.sin(tv[1]), zv[1]],
        [rv[1]*np.cos(tv[0]), rv[1]*np.sin(tv[0]), zv[1]]
    ])
    return v

def create_cv_trimesh(rv, tv, zv):
    v = get_cv_vertices(rv, tv, zv)
    faces = [
        [0, 1, 2], [0, 2, 3], 
        [4, 6, 5], [4, 7, 6], 
        [0, 4, 5], [0, 5, 1], 
        [3, 2, 6], [3, 6, 7], 
        [0, 3, 7], [0, 7, 4], 
        [1, 5, 6], [1, 6, 2]  
    ]
    return trimesh.Trimesh(vertices=v, faces=faces, process=False)

def calculate_geometric_error_boolean(r_nodes, theta_nodes, z_nodes, mask_A):
    print("\n--- Bắt đầu tính toán sai số hình học bằng Boolean 3D ---")
    print("Cảnh báo: Quá trình này có thể mất vài phút tùy thuộc vào số lượng CV...")

    box_exact = trimesh.creation.box(extents=EXTENTS)
    box_exact.apply_translation(CENTER_OFFSET)
    vol_exact = box_exact.volume

    total_cv_a = np.sum(mask_A)
    total_cells = mask_A.size
    
    vol_loi_ra = 0.0  
    vol_khuyet_vao = 0.0 

    count = 0
    for i in range(len(r_nodes)-1):
        for j in range(len(theta_nodes)-1):
            for k in range(len(z_nodes)-1):
                count += 1
                sys.stdout.write(f"\rĐang xử lý CV: {count}/{total_cells}")
                sys.stdout.flush()

                cv_v = get_cv_vertices(r_nodes[i:i+2], theta_nodes[j:j+2], z_nodes[k:k+2])
                min_cv = np.min(cv_v, axis=0)
                max_cv = np.max(cv_v, axis=0)
                min_box = box_exact.bounds[0]
                max_box = box_exact.bounds[1]
                
                if (np.any(min_cv > max_box) or np.any(max_cv < min_box)):
                    continue

                cv_mesh = create_cv_trimesh(r_nodes[i:i+2], theta_nodes[j:j+2], z_nodes[k:k+2])
                is_type_A = mask_A[i, j, k]

                try:
                    intersection = cv_mesh.intersection(box_exact)
                    v_in = intersection.volume if intersection.is_volume else 0.0
                except Exception:
                    v_in = 0.0
                
                v_cv = cv_mesh.volume

                if is_type_A:
                    vol_loi_ra += (v_cv - v_in)
                else:
                    vol_khuyet_vao += v_in

    print("\n\n--- KẾT QUẢ RỜI RẠC HÓA ---")
    print(f"Tổng số Control Volumes (Toàn miền): {total_cells}")
    print(f"Số lượng CV Vật liệu A (Bên trong hộp): {total_cv_a}")
    print(f"Thể tích hộp lý thuyết (Exact): {vol_exact:.6f}")
    print(f"Tổng thể tích lòi ra (Over-estimation): {vol_loi_ra:.6f}")
    print(f"Tổng thể tích khuyết vào (Under-estimation): {vol_khuyet_vao:.6f}")
    
    total_error = vol_loi_ra + vol_khuyet_vao
    error_percentage = (total_error / vol_exact) * 100
    print(f"-> TỔNG SAI SỐ HÌNH HỌC TỐI ĐA: {total_error:.6f} ({error_percentage:.2f}%)")
    print("---------------------------------------------------------")
    
    return total_cells, error_percentage

def plot_matplotlib(r_nodes, theta_nodes, z_nodes, mask_A, total_cells, error_percentage):
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('white')

    ax.set_title(f"Tổng số phần tử: {total_cells} | Sai số hình học: {error_percentage:.2f}%", fontsize=14, fontweight='bold', pad=20)

    all_faces = []
    indices = np.argwhere(mask_A)
    for i, j, k in indices:
        v = get_cv_vertices(r_nodes[i:i+2], theta_nodes[j:j+2], z_nodes[k:k+2])
        faces = [v[[0,1,2,3]], v[[4,5,6,7]], v[[0,1,5,4]], v[[1,2,6,5]], v[[2,3,7,6]], v[[3,0,4,7]]]
        all_faces.extend(faces)
    
    if all_faces:
        poly = Poly3DCollection(all_faces, facecolors=COLOR_A, edgecolors='black', 
                                linewidths=0.2, alpha=OPACITY_A, antialiased=True)
        ax.add_collection3d(poly)

    if SHOW_GRID:
        for r in r_nodes: 
            for z in z_nodes:
                ax.plot(r*np.cos(theta_nodes), r*np.sin(theta_nodes), z, color='black', alpha=GRID_OPACITY, lw=0.3)
        
        for th in theta_nodes:
            for z in z_nodes:
                ax.plot([r_nodes[0]*np.cos(th), r_nodes[-1]*np.cos(th)], 
                        [r_nodes[0]*np.sin(th), r_nodes[-1]*np.sin(th)], z, color='black', alpha=GRID_OPACITY, lw=0.3)

        for r in r_nodes:
            for th in theta_nodes:
                ax.plot([r*np.cos(th), r*np.cos(th)], [r*np.sin(th), r*np.sin(th)], 
                        [z_nodes[0], z_nodes[-1]], color='black', alpha=GRID_OPACITY, lw=0.3)

    ax.view_init(elev=30, azim=45) 
    ax.set_axis_off()
    limit_max = R_LIMITS[1]
    
    ax.set_xlim(0, limit_max); ax.set_ylim(0, limit_max); ax.set_zlim(Z_LIMITS[0], Z_LIMITS[1])
    ax.set_box_aspect((limit_max, limit_max, Z_LIMITS[1] - Z_LIMITS[0]))
    plt.show()

def plot_original_only(r_nodes, theta_nodes, z_nodes):
    box_exact = trimesh.creation.box(extents=EXTENTS)
    box_exact.apply_translation(CENTER_OFFSET)

    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('white')
    ax.set_title("Hình hộp lý thuyết (Original Box)", fontsize=14, fontweight='bold', pad=20)
    
    x_min = CENTER_OFFSET[0] - EXTENTS[0]/2
    x_max = CENTER_OFFSET[0] + EXTENTS[0]/2
    y_min = CENTER_OFFSET[1] - EXTENTS[1]/2
    y_max = CENTER_OFFSET[1] + EXTENTS[1]/2
    z_min = CENTER_OFFSET[2] - EXTENTS[2]/2
    z_max = CENTER_OFFSET[2] + EXTENTS[2]/2

    v_box = np.array([
        [x_min, y_min, z_min],
        [x_max, y_min, z_min],
        [x_max, y_max, z_min],
        [x_min, y_max, z_min],
        [x_min, y_min, z_max],
        [x_max, y_min, z_max],
        [x_max, y_max, z_max],
        [x_min, y_max, z_max]
    ])

    faces_box = [
        [v_box[0], v_box[1], v_box[2], v_box[3]], # Bottom
        [v_box[4], v_box[5], v_box[6], v_box[7]], # Top
        [v_box[0], v_box[1], v_box[5], v_box[4]], # Front
        [v_box[1], v_box[2], v_box[6], v_box[5]], # Right
        [v_box[2], v_box[3], v_box[7], v_box[6]], # Back
        [v_box[3], v_box[0], v_box[4], v_box[7]]  # Left
    ]

    normals = np.array([
        [0, 0, -1],
        [0, 0, 1],
        [0, -1, 0],
        [1, 0, 0],
        [0, 1, 0],
        [-1, 0, 0]
    ])

    base_rgb = np.array(mcolors.to_rgb(COLOR_A))
    light_dir = np.array([1.0, 1.0, 2.0])
    light_dir = light_dir / np.linalg.norm(light_dir)
    intensities = np.clip(np.dot(normals, light_dir) * 0.15 + 0.85, 0, 1)
    face_colors = base_rgb * intensities[:, np.newaxis]

    poly = Poly3DCollection(faces_box, facecolors=face_colors, edgecolors='none', alpha=OPACITY_A, antialiased=True)
    poly.set_zsort('average')
    ax.add_collection3d(poly)

    limit_max = R_LIMITS[1]
    ax.set_xlim(0, limit_max); ax.set_ylim(0, limit_max); ax.set_zlim(Z_LIMITS[0], Z_LIMITS[1])
    ax.set_box_aspect((limit_max, limit_max, Z_LIMITS[1] - Z_LIMITS[0]))
    ax.view_init(elev=30, azim=45) 
    ax.set_axis_off()
    plt.show()

if __name__ == "__main__":
    r_n = np.linspace(R_LIMITS[0], R_LIMITS[1], N_R)
    t_n = np.linspace(THETA_LIMITS[0], THETA_LIMITS[1], N_THETA)
    z_n = np.linspace(Z_LIMITS[0], Z_LIMITS[1], N_Z)

    if SHOW_ORIGINAL:
        plot_original_only(r_n, t_n, z_n)
    else:
        rc, tc, zc = np.meshgrid((r_n[:-1]+r_n[1:])/2, (t_n[:-1]+t_n[1:])/2, (z_n[:-1]+z_n[1:])/2, indexing='ij')
        xc, yc = rc * np.cos(tc), rc * np.sin(tc)
        
        mask = (np.abs(xc - CENTER_OFFSET[0]) <= EXTENTS[0]/2) & \
               (np.abs(yc - CENTER_OFFSET[1]) <= EXTENTS[1]/2) & \
               (np.abs(zc - CENTER_OFFSET[2]) <= EXTENTS[2]/2)

        total_cells, error_percentage = calculate_geometric_error_boolean(r_n, t_n, z_n, mask)

        plot_matplotlib(r_n, t_n, z_n, mask, total_cells, error_percentage)