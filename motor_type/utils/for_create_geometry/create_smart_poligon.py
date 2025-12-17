import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# ==========================================
# 1. CÁC HÀM PHỤ TRỢ
# ==========================================

def resample_path_2d(path, target_count):
    """Nội suy lại đường cong 2D."""
    if len(path) == target_count: return path
    
    # Tính khoảng cách dồn tích
    dists = np.sqrt(np.sum(np.diff(path, axis=0)**2, axis=1))
    cum_dist = np.concatenate(([0], np.cumsum(dists)))
    
    # Nội suy
    new_dists = np.linspace(0, cum_dist[-1], target_count)
    new_x = np.interp(new_dists, cum_dist, path[:, 0])
    new_y = np.interp(new_dists, cum_dist, path[:, 1])
    
    return np.column_stack((new_x, new_y))

def create_arc_helper(radius, start_rad, end_rad, num_points):
    """Hàm tạo cung tròn nhanh để test."""
    t = np.linspace(start_rad, end_rad, num_points)
    return np.column_stack((radius * np.cos(t), radius * np.sin(t)))

# ==========================================
# 2. HÀM CHÍNH: CREATE SMART POLYGON
# ==========================================

def create_smart_polygon(arc1, arc2):
    """
    Nối 2 cung tròn (mảng điểm 2D) thành một Polygon khép kín.
    Tự động xử lý: Chênh lệch số điểm & Ngược chiều.
    """
    # 1. Chuẩn hóa
    arc1 = np.array(arc1, dtype=np.float64)
    arc2 = np.array(arc2, dtype=np.float64)

    if arc1.shape[1] != 2 or arc2.shape[1] != 2:
        raise ValueError("Input phải là mảng 2D (x, y).")

    # 2. Resampling (Ưu tiên giữ độ mịn cao nhất)
    n1, n2 = len(arc1), len(arc2)
    if n1 != n2:
        target = max(n1, n2) 
        if n1 != target: arc1 = resample_path_2d(arc1, target)
        if n2 != target: arc2 = resample_path_2d(arc2, target)

    # 3. Smart Direction (Nối vòng kín)
    # Logic: Đi hết Arc1, điểm tiếp theo phải là điểm GẦN NHẤT của Arc2
    end1 = arc1[-1]
    start2 = arc2[0]
    end2 = arc2[-1]

    dist_to_start = np.linalg.norm(end1 - start2)
    dist_to_end   = np.linalg.norm(end1 - end2)

    if dist_to_end < dist_to_start:
        #print(">> [INFO] Đảo chiều Arc 2 để khép vòng Polygon.")
        arc2 = arc2[::-1]
    
    # 4. Tạo Polygon
    # Nối chuỗi: Arc1 -> Arc2 -> (Tự động về đầu)
    closed_loop = np.vstack((arc1, arc2))
    
    return Polygon(closed_loop)

# ==========================================
# 3. HÀM VẼ (MATPLOTLIB)
# ==========================================

def plot_polygon_matplotlib(poly, title="Shapely Polygon"):
    """Vẽ đối tượng Shapely Polygon bằng Matplotlib."""
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Lấy tọa độ đường bao ngoài
    x, y = poly.exterior.xy
    
    # 1. Vẽ đường viền
    ax.plot(x, y, color='blue', linewidth=2, label='Boundary')
    
    # 2. Tô màu bên trong (Fill)
    ax.fill(x, y, alpha=0.3, fc='cyan', label='Interior')
    
    # 3. Vẽ các điểm dữ liệu để kiểm tra độ mịn
    ax.scatter(x, y, color='red', s=10, marker='.', label='Vertices')

    # Căn chỉnh tỷ lệ 1:1 để hình tròn không bị méo thành elip
    ax.set_aspect('equal')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()
    ax.set_title(title)
    
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.show()

# ==========================================
# 4. CHẠY TEST
# ==========================================
if __name__ == "__main__":
    print("--- TEST: Create Polygon from Arcs ---")

    # CASE: Tạo hình "Vành khuyên cắt" (Sector/Annulus Segment)
    # Cung trong: R=10, 0 -> 90 độ (Mịn: 50 điểm)
    inner = create_arc_helper(10, 0, np.pi/2, 50)
    
    # Cung ngoài: R=20, 0 -> 90 độ (Thô: 10 điểm)
    # CỐ TÌNH: Chạy ngược chiều (90 -> 0) để test tính năng đảo chiều
    outer = create_arc_helper(20, np.pi/2, 0, 10)

    print(f"Input: Inner ({len(inner)} pts) vs Outer ({len(outer)} pts)")

    try:
        # Gọi hàm
        poly = create_smart_polygon(inner, outer)
        
        print(">> Polygon Created Successfully!")
        print(f"   Area: {poly.area:.2f}")
        print(f"   Perimeter: {poly.length:.2f}")
        print(f"   Is Valid: {poly.is_valid} (Không tự cắt)")
        
        # Vẽ
        plot_polygon_matplotlib(poly, title="Smart Polygon Result (Matplotlib)")

    except Exception as e:
        print(f"Lỗi: {e}")