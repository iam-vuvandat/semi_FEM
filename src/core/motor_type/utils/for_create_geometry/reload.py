from src.core.motor_type.models.Container import Container


def reload(motor,
           reload_winding = False,
           reload_geometry = False,
           reload_mechanical = False,
           reload_calculation_data = False,
           reload_mesh = False,
           reload_material = False,
           reload_reluctance_network = False,
           reload_drive = False):

    state = motor.ready_state

    # Thứ tự phụ thuộc chuẩn: 
    # winding -> material -> geometry -> mechanical -> calculation_data -> mesh -> reluctance_network -> drive

    if reload_winding:
        motor.create_winding()
        state.winding_data = True
        # Vô hiệu hóa toàn bộ chuỗi phía sau
        state.material_database = False
        state.geometry = False
        state.mechanical = False
        state.calculation_data = False
        state.mesh = False
        state.reluctance_network = False
        state.drive = False

    if reload_material:
        motor.create_material_database()
        state.material_database = True
        # Vô hiệu hóa từ geometry trở đi
        state.geometry = False
        state.mechanical = False
        state.calculation_data = False
        state.mesh = False
        state.reluctance_network = False
        state.drive = False

    if reload_geometry:
        motor.create_geometry()
        state.geometry = True
        # Khi hình học đổi, cơ khí và các bước lưới/giải toán phía sau đều mất hiệu lực
        state.mechanical = False
        state.calculation_data = False
        state.mesh = False
        state.reluctance_network = False
        state.drive = False

    if reload_mechanical:
        motor.create_mechanical()
        state.mechanical = True
        # Cơ khí đổi (vị trí/tốc độ) thường kéo theo mesh và solver phải chạy lại
        state.calculation_data = False
        state.mesh = False
        state.reluctance_network = False
        state.drive = False

    if reload_calculation_data:
        state.calculation_data = True
        # Thay đổi thông số tính toán làm vô hiệu hóa lưới và các kết quả mạng từ trở
        state.mesh = False
        state.reluctance_network = False
        state.drive = False

    if reload_mesh:
        motor.create_adaptive_mesh()
        state.mesh = True
        # Lưới đổi thì mạng từ trở và drive phải nạp lại
        state.reluctance_network = False
        state.drive = False

    if reload_reluctance_network:
        motor.create_reluctance_network()
        state.reluctance_network = True
        # Mạng từ trở đổi thì drive phải cập nhật theo
        state.drive = False

    if reload_drive:
        motor.create_drive()
        state.drive = True

    return motor