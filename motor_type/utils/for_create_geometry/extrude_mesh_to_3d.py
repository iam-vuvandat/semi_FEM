import paths
import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# Import các hàm tiện ích
from motor_type.utils.for_create_geometry.create_arc import create_arc
from motor_type.utils.for_create_geometry.create_smart_surface import create_smart_surface

# ==========================================
# HÀM CHÍNH: EXTRUDE (ĐÃ SỬA LỖI)
# ==========================================
def extrude_mesh_to_3d(surface_mesh, height):
    """
    Kéo một bề mặt phẳng (Surface Mesh) lên cao để tạo thành khối đặc (Solid).
    
    Cải tiến: Sử dụng outline() để lấy biên dạng, tương thích mọi phiên bản trimesh.
    """
    # 1. Kiểm tra và chuẩn hóa đầu vào (Fix lỗi Tuple)
    if not isinstance(surface_mesh, trimesh.Trimesh):
        if isinstance(surface_mesh, tuple):
            surface_mesh = trimesh.Trimesh(vertices=surface_mesh[0], faces=surface_mesh[1])
        else:
            raise TypeError(f"Input phải là trimesh.Trimesh, nhận được: {type(surface_mesh)}")

    try:
        # --- BƯỚC QUAN TRỌNG: LẤY BIÊN DẠNG 2D ---
        # Thay vì dùng project_to_plane (gây lỗi), ta dùng outline()
        # outline() trả về đối tượng Path3D chứa các cạnh biên
        path_3d = surface_mesh.outline()
        
        if path_3d is None or len(path_3d.entities) == 0:
            raise ValueError("Không tìm thấy đường bao (Mesh có thể bị hở hoặc không phẳng).")

        # Chuyển Path3D thành Path2D (phẳng)
        # to_planar() trả về (Path2D, TransformationMatrix)
        path_2d, _ = path_3d.to_planar()
        
        # Lấy danh sách các đa giác (bao gồm cả vỏ ngoài và lỗ rỗng)
        polygons = path_2d.polygons_full 
        
        if len(polygons) == 0:
            raise ValueError("Không tạo được Polygon từ đường bao.")

        # --- BƯỚC 2: ĐÙN KHỐI TỪ POLYGON ---
        solid_parts = []
        for poly in polygons:
            # extrude_polygon tự động tạo: Nắp trên + Nắp dưới + Vách tường
            # Kết quả là một khối đặc (Watertight)
            part = trimesh.creation.extrude_polygon(poly, height=height)
            
            # --- BƯỚC 3: DỊCH CHUYỂN VỀ VỊ TRÍ CŨ ---
            # extrude_polygon luôn tạo vật thể bắt đầu từ Z=0 cục bộ.
            # Ta cần đưa nó về đúng độ cao Z của surface_mesh gốc.
            z_origin = surface_mesh.bounds[0][2] 
            part.apply_translation([0, 0, z_origin])
            
            solid_parts.append(part)
            
        # Gộp các phần (nếu có nhiều mảnh rời rạc)
        if len(solid_parts) == 1:
            return solid_parts[0]
        else:
            final_mesh = trimesh.util.concatenate(solid_parts)
            final_mesh.merge_vertices()
            return final_mesh

    except Exception as e:
        print(f"⚠️ Lỗi đùn khối thông minh: {e}")
        print(">> Đang dùng phương pháp Fallback (Ghép nắp thủ công - Sẽ không kín)...")
        
        # Fallback: Copy mặt đáy và đỉnh (Chỉ dùng khi bí quá)
        bottom = surface_mesh.copy()
        top = surface_mesh.copy()
        top.apply_translation([0, 0, height])
        
        # Lưu ý: Fallback này sẽ tạo ra mesh RỖNG (không có vách tường)
        return trimesh.util.concatenate([bottom, top])

# ==========================================
# HÀM VẼ (HELPER)
# ==========================================
def plot_mesh(mesh, title="Result"):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Vẽ đa giác
    polygons = mesh.vertices[mesh.faces]
    col = Poly3DCollection(polygons, alpha=0.8, linewidths=0.1, edgecolor='k')
    col.set_facecolor((0.2, 0.8, 0.8)) # Màu Cyan
    ax.add_collection3d(col)

    # Căn chỉnh trục
    b = mesh.bounds
    mid = (b[0]+b[1])*0.5; rng = (b[1]-b[0]).max()/2
    ax.set_xlim(mid[0]-rng, mid[0]+rng)
    ax.set_ylim(mid[1]-rng, mid[1]+rng)
    ax.set_zlim(mid[2]-rng, mid[2]+rng)
    
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
    plt.title(title)
    plt.show()

# ==========================================
# PHẦN TEST CHÍNH
# ==========================================
if __name__ == "__main__":
    print("--- TEST: EXTRUDE FROM SMART SURFACE (FIXED) ---")

    # 1. TẠO DỮ LIỆU BẰNG HÀM CỦA BẠN
    print("1. Đang tạo 2 cung tròn...")
    arc_inner = create_arc(radius=10, start_rad=0, end_rad=np.pi, num_points=50)
    arc_outer = create_arc(radius=20, start_rad=0, end_rad=np.pi, num_points=50)

    # 2. TẠO MẶT PHẲNG (Surface Mesh)
    # Đặt lơ lửng tại Z=15
    print("2. Đang nối thành bề mặt phẳng (Z=15)...")
    flat_surface = create_smart_surface(
        arc1=arc_inner, 
        arc2=arc_outer, 
        z1=15.0, 
        z2=15.0 # Z bằng nhau -> Mặt phẳng
    )
    
    print(f"   Input Surface Vertices: {len(flat_surface.vertices)}")
    
    # 3. GỌI HÀM EXTRUDE (Đã sửa lỗi)
    try:
        print("3. Đang đùn khối (Extrude) lên cao 30 đơn vị...")
        # Kéo từ Z=15 -> Z=45
        solid_mesh = extrude_mesh_to_3d(flat_surface, height=30.0)
        
        # 4. KIỂM TRA KẾT QUẢ
        z_min = solid_mesh.bounds[0][2]
        z_max = solid_mesh.bounds[1][2]
        
        print("-" * 30)
        print(f"   >>> DONE! Solid Mesh Created.")
        print(f"   Watertight (Kín nước): {solid_mesh.is_watertight} (True là thành công)")
        print(f"   Z Min: {z_min:.2f} (Kỳ vọng: 15.0)")
        print(f"   Z Max: {z_max:.2f} (Kỳ vọng: 45.0)")
        print("-" * 30)
        
        # 5. VẼ
        plot_mesh(solid_mesh, title="Extruded Annulus (Z: 15->45)")
        
    except Exception as e:
        print(f"Lỗi: {e}")