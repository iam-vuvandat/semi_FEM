def disable_excitation(m3d, current):
    """
    Vô hiệu hóa kích thích bằng cách gán dòng điện về 0.
    Tránh sử dụng get_all_sources() để hạn chế lỗi gRPC khi model chưa giải.
    """
    # oboundary là property chuẩn để truy cập module BoundarySetup/BoundarySetup1
    boundary_module = m3d.oboundary

    for winding in current:
        # Gán giá trị 0 cho thuộc tính Current của Winding
        # Việc gán về 0 sẽ tự động cập nhật cho tất cả các Coil con bên trong
        boundary_module.Edit(winding.name, [
            f"NAME:{winding.name}",
            "Current:=", "0"
        ])