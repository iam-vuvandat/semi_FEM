import numpy as np

def create_arc(radius, start_rad, end_rad, num_points=100):
    """
    Tạo đường cong cung tròn 2D (x, y).
    
    Tham số:
    - radius: Bán kính.
    - start_rad: Góc bắt đầu (Radian).
    - end_rad: Góc kết thúc (Radian).
    - num_points: Độ mịn (số điểm).
    """
    t = np.linspace(start_rad, end_rad, num_points)
    x = radius * np.cos(t)
    y = radius * np.sin(t)
    
    return np.column_stack((x, y))

# --- CÁCH SỬ DỤNG ---
if __name__ == "__main__":
    # Thay thế 2 dòng cũ của bạn bằng 1 dòng này:
    # curve_a = np.column_stack((10*np.cos(t1), 10*np.sin(t1)))
    
    curve_a = create_arc(radius=10, start_rad=0, end_rad=np.pi, num_points=100)
    
    print(f"Shape của curve_a: {curve_a.shape}") # Kết quả: (100, 2)
    print(curve_a)