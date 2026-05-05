def view_iso(viewer_state):
    # Sử dụng vector chuẩn của Ansys Maxwell cho góc nhìn Isometric
    default_view_scale = (0.494, -0.714, 0.493)
    cx = default_view_scale[0] * viewer_state.dist_factor
    cy = default_view_scale[1] * viewer_state.dist_factor
    cz = default_view_scale[2] * viewer_state.dist_factor
    
    # Thiết lập vị trí camera, tiêu điểm (gốc tọa độ) và hướng Z làm hướng Up (view up)
    viewer_state.pl.camera_position = [(cx, cy, cz), (0, 0, 0), (0, 0, 1)]
    viewer_state.render()