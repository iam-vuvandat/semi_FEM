import numpy as np
import trimesh
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ==========================================
# 1. HÀM CHÍNH: EXTRUDE GIỮA 2 ĐỘ CAO Z
# ==========================================

def extrude_polygon_between_z(polygon, z1, z2):
    """
    Tạo khối 3D (Trimesh) bằng cách đùn một Polygon 2D từ độ cao z1 đến z2.
    
    Tham số:
    - polygon: Đối tượng shapely.geometry.Polygon (2D).
    - z1: Độ cao mặt đáy (Bottom Z).
    - z2: Độ cao mặt đỉnh (Top Z).
    
    Trả về:
    - trimesh.Trimesh: Khối đặc nằm giữa z1 và z2.
    """
    # 1. Kiểm tra đầu vào
    if not isinstance(polygon, Polygon):
        raise TypeError("Input phải là đối tượng shapely.geometry.Polygon.")
    
    # Đảm bảo z2 luôn lớn hơn z1 để tính chiều cao dương
    if z1 > z2:
        z1, z2 = z2, z1 # Hoán đổi nếu ngược
        print(f">> [INFO] Đã tự động hoán đổi z1, z2: Đáy={z1}, Đỉnh={z2}")
    
    height = z2 - z1
    
    if height <= 0:
        raise ValueError("Chiều cao đùn khối (z2 - z1) phải lớn hơn 0.")

    # 2. Đùn khối (Extrude)
    # Hàm này tạo ra mesh có đáy tại Z=0 và đỉnh tại Z=height
    mesh = trimesh.creation.extrude_polygon(polygon, height=height)
    
    # 3. Dịch chuyển về đúng vị trí z1
    # Mặc định extrude_polygon tạo vật thể có đáy nằm trên mặt phẳng XY (Z=0)
    mesh.apply_translation([0, 0, z1])
    
    return mesh

# ==========================================
# 2. HÀM VẼ (MATPLOTLIB)
# ==========================================
def plot_mesh(mesh, title="Extruded Result"):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Lấy đa giác từ mesh
    polygons = mesh.vertices[mesh.faces]
    
    # Tạo Collection
    mesh_col = Poly3DCollection(polygons, alpha=0.8, linewidths=0.1, edgecolor='k')
    mesh_col.set_facecolor((0.2, 0.7, 0.5)) # Màu xanh ngọc
    ax.add_collection3d(mesh_col)

    # Căn chỉnh trục (Auto-scale)
    bounds = mesh.bounds
    mid = (bounds[0] + bounds[1]) * 0.5
    rng = (bounds[1] - bounds[0]).max() / 2.0
    
    ax.set_xlim(mid[0]-rng, mid[0]+rng)
    ax.set_ylim(mid[1]-rng, mid[1]+rng)
    ax.set_zlim(mid[2]-rng, mid[2]+rng)
    
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
    plt.title(title)
    plt.show()

# ==========================================
# 3. SCRIPT TEST
# ==========================================
if __name__ == "__main__":
    # Import hàm tạo Polygon thông minh từ bài trước (để test cho đẹp)
    # Hoặc tạo Polygon thủ công ở đây
    
    print("--- TEST: Extrude Polygon between Z1 and Z2 ---")

    # 1. Tạo một Polygon hình chữ C (Concave) để test độ khó
    # (Hình vành khăn bị cắt một góc)
    t = np.linspace(0, 1.5*np.pi, 50) # Cung 270 độ
    outer = np.column_stack((20*np.cos(t), 20*np.sin(t)))
    inner = np.column_stack((10*np.cos(t), 10*np.sin(t)))[::-1] # Đảo chiều để nối vòng
    
    # Nối thành vòng kín
    pts = np.vstack((outer, inner, outer[0])) 
    poly_shape = Polygon(pts)
    
    if not poly_shape.is_valid:
        # Fix lỗi tự cắt nếu có (thường do nối điểm cuối chưa chuẩn)
        poly_shape = poly_shape.buffer(0) 

    # 2. Định nghĩa độ cao mong muốn
    Z_BOTTOM = 15.0
    Z_TOP = 40.0
    
    try:
        print(f"1. Input: Polygon 2D (Area={poly_shape.area:.1f})")
        print(f"2. Action: Extrude từ Z={Z_BOTTOM} đến Z={Z_TOP}")
        
        # GỌI HÀM
        solid_mesh = extrude_polygon_between_z(poly_shape, z1=Z_BOTTOM, z2=Z_TOP)
        
        # KIỂM TRA KẾT QUẢ
        z_min_real = solid_mesh.bounds[0][2]
        z_max_real = solid_mesh.bounds[1][2]
        
        print("-" * 30)
        print(f"   >>> DONE! Mesh Created.")
        print(f"   Vertices:   {len(solid_mesh.vertices)}")
        print(f"   Watertight: {solid_mesh.is_watertight}")
        print(f"   Z Min Thực tế: {z_min_real:.2f} (Kỳ vọng: {Z_BOTTOM})")
        print(f"   Z Max Thực tế: {z_max_real:.2f} (Kỳ vọng: {Z_TOP})")
        print("-" * 30)
        
        # Vẽ
        plot_mesh(solid_mesh, title=f"Extruded Solid (Z: {Z_BOTTOM} -> {Z_TOP})")
        
    except Exception as e:
        print(f"Lỗi: {e}")