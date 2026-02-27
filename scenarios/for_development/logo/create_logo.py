import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from mpl_toolkits.mplot3d import art3d

def draw_logo_v2():
    """
    Vẽ logo biểu đồ tròn phân mảnh dưới dạng các hình khối liền mạch.
    """
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Dữ liệu màu sắc, giữ nguyên từ hình ảnh gốc
    colors = ['#87CEEB', '#4169E1', '#2980B9', '#3498DB']
    
    # Kích thước mỗi mảnh (4 phần bằng nhau)
    sizes = [25, 25, 25, 25]
    
    # Chiều cao của khối cho mỗi mảnh. Mảnh cyan (trên cùng bên phải) cao hơn.
    heights = [1.2, 0.4, 0.4, 0.4] 
    
    # Các thông số hình học của logo
    inner_radius = 0.5
    outer_radius = 1.0
    start_angle = 90  # Bắt đầu từ góc 12 giờ
    
    # Duyệt qua từng mảnh để vẽ
    for i, size in enumerate(sizes):
        end_angle = start_angle + (size * 3.6)
        
        # 1. Vẽ mặt trên và mặt dưới
        # Wedge (hình quạt) cho mặt trên (ở cao độ heights[i])
        w_top = Wedge((0, 0), outer_radius, start_angle, end_angle, 
                      facecolor=colors[i], edgecolor=colors[i], alpha=1.0)
        # Wedge (hình quạt) cho mặt dưới (ở cao độ 0)
        w_bottom = Wedge((0, 0), outer_radius, start_angle, end_angle, 
                        facecolor=colors[i], edgecolor=colors[i], alpha=1.0)
        
        # 2. Tạo hiệu ứng khối liền: Vẽ các bức tường bao quanh mảnh
        # Bức tường trong (chính xác bằng Wedge có width)
        wall_inner = Wedge((0, 0), outer_radius, start_angle, end_angle, 
                          width=(outer_radius - inner_radius), 
                          facecolor=colors[i], edgecolor=colors[i], alpha=1.0)
        # Bức tường ngoài (phủ kín)
        wall_outer = Wedge((0, 0), outer_radius + 0.01, start_angle, end_angle, 
                          facecolor=colors[i], edgecolor=colors[i], alpha=1.0)
        
        # 3. Chuyển đổi các hình 2D thành 3D ở đúng vị trí và chiều cao
        ax.add_patch(wall_inner)
        art3d.pathpatch_2d_to_3d(wall_inner, z=0, zdir="z")
        
        ax.add_patch(wall_outer)
        art3d.pathpatch_2d_to_3d(wall_outer, z=0, zdir="z")
        
        ax.add_patch(w_bottom)
        art3d.pathpatch_2d_to_3d(w_bottom, z=0, zdir="z")
        
        ax.add_patch(w_top)
        art3d.pathpatch_2d_to_3d(w_top, z=heights[i], zdir="z")
        
        # 4. Thêm các bức tường bên (Radial Walls)
        # Bức tường bên trái
        radial_w_left = Wedge((0, 0), outer_radius, start_angle, start_angle + 0.1, 
                              width=outer_radius, facecolor=colors[i], edgecolor=colors[i], alpha=1.0)
        ax.add_patch(radial_w_left)
        art3d.pathpatch_2d_to_3d(radial_w_left, z=0, zdir="z")
        
        # Bức tường bên phải
        radial_w_right = Wedge((0, 0), outer_radius, end_angle - 0.1, end_angle, 
                               width=outer_radius, facecolor=colors[i], edgecolor=colors[i], alpha=1.0)
        ax.add_patch(radial_w_right)
        art3d.pathpatch_2d_to_3d(radial_w_right, z=0, zdir="z")
        
        # Thêm một chút độ dày cho các bức tường bằng cách lặp lại
        radial_w_left_top = Wedge((0, 0), outer_radius, start_angle, start_angle + 0.1, 
                                   width=outer_radius, facecolor=colors[i], edgecolor=colors[i], alpha=1.0)
        ax.add_patch(radial_w_left_top)
        art3d.pathpatch_2d_to_3d(radial_w_left_top, z=heights[i], zdir="z")
        
        radial_w_right_top = Wedge((0, 0), outer_radius, end_angle - 0.1, end_angle, 
                                    width=outer_radius, facecolor=colors[i], edgecolor=colors[i], alpha=1.0)
        ax.add_patch(radial_w_right_top)
        art3d.pathpatch_2d_to_3d(radial_w_right_top, z=heights[i], zdir="z")
        
        # Cập nhật góc bắt đầu cho mảnh tiếp theo
        start_angle = end_angle

    # Thiết lập khung nhìn để giống với hình ảnh gốc nhất
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_zlim(0, 1.5)
    
    # Ẩn các trục tọa độ
    ax.set_axis_off()
    
    # Góc nhìn tốt nhất để thấy được khối liền và sự khác biệt về chiều cao
    ax.view_init(elev=35, azim=-45)

    plt.show()

if __name__ == "__main__":
    draw_logo_v2()