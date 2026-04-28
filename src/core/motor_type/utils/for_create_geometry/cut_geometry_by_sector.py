import trimesh
import numpy as np
from shapely.geometry import Polygon, Point

def cut_geometry_by_sector(target_mesh, sector_mesh):
    """Cắt đối tượng target_mesh bằng khối sector_mesh"""
    if not target_mesh.is_watertight:
        target_mesh.fill_holes()
        
    try:
        return target_mesh.intersection(sector_mesh, engine='manifold')
    except Exception as e:
        print(f"Manifold engine failed: {e}. Sử dụng engine mặc định...")
        return target_mesh.intersection(sector_mesh)

def create_sector_wedge(radius_max, z_min, z_max, angle_deg):
    """Tạo khối hình rẻ quạt (Wedge) dùng để giới hạn vùng cắt"""
    angle_rad = np.radians(angle_deg)
    points = [[0, 0]]
    for a in np.linspace(0, angle_rad, 50):
        points.append([radius_max * np.cos(a), radius_max * np.sin(a)])
        
    poly = Polygon(points)
    height = z_max - z_min
    sector = trimesh.creation.extrude_polygon(poly, height=height)
    sector.apply_translation([0, 0, z_min])
    return sector

if __name__ == "__main__":
    print("1. Khởi tạo khối 360 độ (Giả lập Stator Yoke)...")
    outer_circle = Point(0, 0).buffer(95.0, resolution=64)
    inner_circle = Point(0, 0).buffer(85.0, resolution=64)
    annulus_2d = outer_circle.difference(inner_circle)

    full_mesh = trimesh.creation.extrude_polygon(annulus_2d, height=20.0)
    full_mesh.apply_translation([0, 0, 10.0])

    sym_factor = 6
    angle_deg = 360.0 / sym_factor
    
    print(f"2. Tạo khối cắt giới hạn (Sector Wedge) với góc {angle_deg} độ...")
    sector_mesh = create_sector_wedge(radius_max=150.0, z_min=0.0, z_max=50.0, angle_deg=angle_deg)

    print("3. Thực hiện Boolean Intersection...")
    cut_mesh = cut_geometry_by_sector(full_mesh, sector_mesh)

    # --- BỔ SUNG: KIỂM TRA KIỂU DỮ LIỆU ĐẦU RA ---
    print("\n--- THÔNG TIN DỮ LIỆU ĐẦU RA ---")
    print(f"Kiểu dữ liệu (Type): {type(cut_mesh)}")
    if isinstance(cut_mesh, trimesh.Trimesh):
        print(f"Số lượng đỉnh (Vertices): {len(cut_mesh.vertices)}")
        print(f"Số lượng mặt (Faces): {len(cut_mesh.faces)}")
        print(f"Thể tích khối (Volume): {cut_mesh.volume:.2f}")
    print("--------------------------------\n")

    print("4. Hiển thị kết quả...")
    full_mesh.visual.face_colors = [200, 200, 200, 50] 
    cut_mesh.visual.face_colors = [255, 50, 50, 255]    

    scene = trimesh.Scene([full_mesh, cut_mesh])
    scene.show()