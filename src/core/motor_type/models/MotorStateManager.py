from src.core.motor_type.models.Container import Container

class MotorStateManager:
    def __init__(self):
        self.ready_state = Container(
            winding_data = False,
            material_database = False,
            geometry     = False,
            mechanical   = False,
            calculation_data = False,
            mesh         = False,
            reluctance_network = False,
            drive        = False
        )
        
        # Thứ tự phụ thuộc logic của máy điện
        self._order = [
            "winding_data", "material_database", "geometry", 
            "mechanical", "calculation_data", "mesh", 
            "reluctance_network", "drive"
        ]
        
        # Ánh xạ thuộc tính sang tham số hàm reload
        self._reload_map = {
            "winding_data": "reload_winding",
            "material_database": "reload_material",
            "geometry": "reload_geometry",
            "mechanical": "reload_mechanical",
            "calculation_data": "reload_calculation_data",
            "mesh": "reload_mesh",
            "reluctance_network": "reload_reluctance_network",
            "drive": "reload_drive"
        }

    def just_changed(self, component_name):
        """Đánh dấu một thành phần đã thay đổi và vô hiệu hóa các cấp thấp hơn."""
        found = False
        for item in self._order:
            if item == component_name:
                found = True
            if found:
                setattr(self.ready_state, item, False)

    def require(self, motor, component_name, callback=None):
        """
        Đảm bảo thành phần yêu cầu sẵn sàng. 
        Nếu phát hiện lỗi thời, tự động triệu hồi chuỗi reload kèm callback.
        """
        for item in self._order:
            if not getattr(self.ready_state, item):
                arg_name = self._reload_map[item]
                kwargs = {arg_name: True}
                # Chuyển tiếp callback vào hàm reload
                self.reload(motor, callback=callback, **kwargs)
            
            if item == component_name:
                break

    def reload(self, motor, callback=None, **kwargs):
        """
        Khởi tạo các thành phần dựa trên flag và thông báo tiến độ qua callback.
        """
        state = self.ready_state

        # Helper nội bộ để gửi thông điệp qua callback
        def send_status(message):
            if callback:
                # Nếu callback là hàm nhận 2 tham số (msg, progress) thì có thể mở rộng sau
                callback(message)

        # 1. Winding
        if kwargs.get('reload_winding'):
            send_status("Generating motor winding analysis...")
            motor.create_winding()
            state.winding_data = True
            self._invalidate_downstream("winding_data")

        # 2. Material
        if kwargs.get('reload_material'):
            send_status("Initializing material database...")
            motor.create_material_database()
            state.material_database = True
            self._invalidate_downstream("material_database")

        # 3. Geometry
        if kwargs.get('reload_geometry'):
            send_status("Creating motor geometry...")
            motor.create_geometry()
            state.geometry = True
            self._invalidate_downstream("geometry")

        # 4. Mechanical
        if kwargs.get('reload_mechanical'):
            send_status("Configuring mechanical properties...")
            motor.create_mechanical()
            state.mechanical = True
            self._invalidate_downstream("mechanical")

        # 5. Calculation Data
        if kwargs.get('reload_calculation_data'):
            send_status("Updating calculation parameters...")
            state.calculation_data = True
            self._invalidate_downstream("calculation_data")

        # 6. Mesh
        if kwargs.get('reload_mesh'):
            send_status("Generating adaptive mesh (this may take a while)...")
            motor.create_adaptive_mesh()
            state.mesh = True
            self._invalidate_downstream("mesh")

        # 7. Reluctance Network
        if kwargs.get('reload_reluctance_network'):
            send_status("Building Reluctance Network model...")
            # Truyền callback sâu xuống nếu class Network có hỗ trợ
            motor.create_reluctance_network(callback=callback)
            state.reluctance_network = True
            self._invalidate_downstream("reluctance_network")

        # 8. Drive
        if kwargs.get('reload_drive'):
            send_status("Applying drive excitation...")
            motor.create_drive()
            state.drive = True

        return motor

    def _invalidate_downstream(self, component_name):
        """Đánh dấu lỗi thời cho tất cả các bước đứng sau bước vừa nạp."""
        found = False
        for item in self._order:
            if found:
                setattr(self.ready_state, item, False)
            if item == component_name:
                found = True