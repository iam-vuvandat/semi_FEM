import numpy as np
import trimesh
from shapely.geometry import Polygon

def create_symmetry_sector(height, radius, symmetry_factor, z_offset=0.0, sections=64):
    """
    Tạo khối 3D hình rẻ quạt (sector) dùng làm khuôn cắt đối xứng.
    """
    # Tính góc mở dựa trên hệ số đối xứng
    angle_rad = 2 * np.pi / symmetry_factor
    
    # Tạo danh sách điểm cho mặt cắt 2D (bắt đầu từ tâm 0,0)
    points = [[0.0, 0.0]]
    
    # Quét cung tròn để tạo hình rẻ quạt
    for a in np.linspace(0, angle_rad, sections):
        points.append([radius * np.cos(a), radius * np.sin(a)])
    
    # Khép kín đa giác và đùn khối (extrude)
    poly = Polygon(points)
    sector_mesh = trimesh.creation.extrude_polygon(poly, height=height)
    
    # Dịch chuyển theo trục Z nếu có yêu cầu
    if z_offset != 0.0:
        sector_mesh.apply_translation([0, 0, z_offset])
        
    return sector_mesh

if __name__ == "__main__":
    # --- THÔNG SỐ TEST ---
    SYM_FACTOR = 6        # Chia 6 (góc 60 độ)
    R_TEST = 100.0        # Bán kính 100mm
    H_TEST = 50.0         # Cao 50mm
    Z_OFF = 10.0          # Đáy nằm tại Z=10
    
    print(f"--- Đang tạo Symmetry Sector (1/{SYM_FACTOR}) ---")
    
    # Gọi hàm tạo khối
    sector = create_symmetry_sector(
        height=H_TEST, 
        radius=R_TEST, 
        symmetry_factor=SYM_FACTOR, 
        z_offset=Z_OFF
    )
    
    # --- KIỂM TRA DỮ LIỆU ---
    print(f"Kiểu dữ liệu: {type(sector)}")
    print(f"Số lượng mặt (Faces): {len(sector.faces)}")
    print(f"Giới hạn trục Z: {sector.bounds[0][2]} đến {sector.bounds[1][2]}")
    
    # Kiểm tra tính kín của Mesh (Quan trọng để cắt Boolean)
    if sector.is_watertight:
        print("Trạng thái: Mesh kín hoàn toàn (Watertight) - Sẵn sàng để cắt.")
    else:
        print("Cảnh báo: Mesh bị hở.")

    # --- HIỂN THỊ ---
    # Đặt màu đỏ trong suốt để dễ quan sát
    sector.visual.face_colors = [255, 50, 50, 150]
    
    # Hiển thị thêm hệ trục tọa độ để kiểm chứng góc xoay
    axis = trimesh.creation.axis(origin_size=5)
    scene = trimesh.Scene([sector, axis])
    scene.show()