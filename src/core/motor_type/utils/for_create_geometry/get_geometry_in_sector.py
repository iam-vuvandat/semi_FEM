import paths
import trimesh
import numpy as np
from shapely.geometry import Polygon, Point

# Import hàm tạo sector từ module cùng thư mục
from src.core.motor_type.utils.for_create_geometry.create_symmetry_sector import create_symmetry_sector

def get_geometry_in_sector(target_mesh, sector_mesh):
    """
    Thực hiện phép giao (Intersection) giữa khối đích và khuôn cắt đối xứng.
    Trả về:
        - target_mesh_cut: Phần vật liệu nằm bên trong sector.
        - state: True nếu có phần giao, False nếu không có gì (rỗng).
    """
    # Đảm bảo mesh kín để phép toán Boolean đạt độ chính xác cao nhất
    if not target_mesh.is_watertight:
        target_mesh.fill_holes()
        
    try:
        # Ưu tiên sử dụng manifold engine cho các tác vụ máy điện phức tạp
        target_mesh_cut = target_mesh.intersection(sector_mesh, engine='manifold')
    except Exception:
        # Fallback về engine mặc định nếu manifold không khả dụng
        target_mesh_cut = target_mesh.intersection(sector_mesh)

    # Kiểm tra trạng thái rỗng của kết quả
    # Một mesh được coi là rỗng nếu thuộc tính is_empty là True hoặc không có mặt (faces)
    state = not target_mesh_cut.is_empty and len(target_mesh_cut.faces) > 0
    
    return target_mesh_cut, state

if __name__ == "__main__":
    # Cấu hình sector chung cho các bài test (Góc 60 độ)
    sym_factor = 6 
    sector_wedge = create_symmetry_sector(
        height=100.0, 
        radius=150.0, 
        symmetry_factor=sym_factor
    )

    # --- TEST 1: VẬT THỂ NẰM GIAO THOA (Overlap) ---
    print("--- TEST 1: Vật thể nằm ở biên (Giao thoa) ---")
    sphere_overlap = trimesh.creation.uv_sphere(radius=30.0)
    sphere_overlap.apply_translation([100.0, 0.0, 50.0])
    
    mesh_1, state_1 = get_geometry_in_sector(sphere_overlap, sector_wedge)
    
    print(f"State: {state_1}")
    print(f"Số lượng mặt thu được: {len(mesh_1.faces)}")

    # --- TEST 2: VẬT THỂ NẰM HOÀN TOÀN BÊN NGOÀI (Outside) ---
    print("\n--- TEST 2: Vật thể nằm hoàn toàn bên ngoài ---")
    sphere_outside = trimesh.creation.uv_sphere(radius=10.0)
    sphere_outside.apply_translation([100.0, -50.0, 50.0])
    
    mesh_2, state_2 = get_geometry_in_sector(sphere_outside, sector_wedge)
    
    print(f"State: {state_2}")
    print(f"Số lượng mặt thu được: {len(mesh_2.faces)}")

    # --- TEST 3: VẬT THỂ NẰM TRONG HOÀN TOÀN (Inside) ---
    print("\n--- TEST 3: Vật thể nằm hoàn toàn bên trong ---")
    sphere_inside = trimesh.creation.uv_sphere(radius=10.0)
    sphere_inside.apply_translation([100.0, 20.0, 50.0])
    
    mesh_3, state_3 = get_geometry_in_sector(sphere_inside, sector_wedge)
    
    print(f"State: {state_3}")
    print(f"Số lượng mặt thu được: {len(mesh_3.faces)}")

    # Hiển thị trực quan cho Test 1 và Test 2
    sector_wedge.visual.face_colors = [200, 200, 200, 30]
    mesh_1.visual.face_colors = [255, 0, 0, 255] # Màu đỏ cho phần giao thoa
    
    scene = trimesh.Scene([sector_wedge, sphere_overlap, mesh_1, sphere_outside])
    scene.show()