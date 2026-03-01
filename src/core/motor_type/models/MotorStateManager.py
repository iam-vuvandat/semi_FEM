from src.core.motor_type.models.Container import Container

class MotorStateManager:
    def __init__(self):
        self.ready_state = Container(
            winding_data      = False,
            material_database = False,
            geometry          = False,
            mechanical        = False,
            calculation_data  = False,
            mesh              = False,
            reluctance_network = False,
            drive             = False
        )
        
        # Thứ tự phụ thuộc tuyến tính (cho các bước sau gốc)
        self._order = [
            "winding_data", "material_database", "geometry", 
            "mechanical", "calculation_data", "mesh", 
            "reluctance_network", "drive"
        ]
        
        # Danh sách các "Gốc" - Thay đổi 1 cái là reset tất cả
        self._root_components = ["winding_data", "geometry"]

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
        """
        Đánh dấu thay đổi. 
        Nếu là geometry hoặc winding_data: Tháo toàn bộ cờ.
        Nếu là các bước khác: Chỉ tháo cờ từ bước đó trở xuống.
        """
        if component_name in self._root_components:
            # Quy tắc đặc biệt: Reset sạch sành sanh
            for item in self._order:
                setattr(self.ready_state, item, False)
        else:
            # Quy tắc thác đổ (Cascade): Tháo từ vị trí đó trở xuống
            found = False
            for item in self._order:
                if item == component_name:
                    found = True
                if found:
                    setattr(self.ready_state, item, False)

    def require(self, motor, component_name, callback=None):
        """Đảm bảo chuỗi phụ thuộc sẵn sàng theo đúng thứ tự."""
        for item in self._order:
            if not getattr(self.ready_state, item):
                arg_name = self._reload_map[item]
                self.reload(motor, callback=callback, **{arg_name: True})
            
            if item == component_name:
                break

    def reload(self, motor, callback=None, **kwargs):
        """Thực thi khởi tạo các thành phần vật lý."""
        state = self.ready_state

        def send_status(msg):
            if callback: callback(msg)

        # 1. Winding
        if kwargs.get('reload_winding'):
            send_status("Generating motor winding analysis...")
            motor.create_winding()
            state.winding_data = True

        # 2. Material
        if kwargs.get('reload_material'):
            send_status("Initializing material database...")
            motor.create_material_database()
            state.material_database = True

        # 3. Geometry
        if kwargs.get('reload_geometry'):
            send_status("Creating motor geometry...")
            motor.create_geometry()
            state.geometry = True

        # 4. Mechanical
        if kwargs.get('reload_mechanical'):
            send_status("Configuring mechanical properties...")
            motor.create_mechanical()
            state.mechanical = True

        # 5. Calculation Data
        if kwargs.get('reload_calculation_data'):
            send_status("Updating calculation parameters...")
            state.calculation_data = True

        # 6. Mesh
        if kwargs.get('reload_mesh'):
            send_status("Generating adaptive mesh...")
            motor.create_adaptive_mesh()
            state.mesh = True

        # 7. Reluctance Network
        if kwargs.get('reload_reluctance_network'):
            send_status("Building Reluctance Network model...")
            motor.create_reluctance_network(callback=callback)
            state.reluctance_network = True

        # 8. Drive
        if kwargs.get('reload_drive'):
            send_status("Applying drive excitation...")
            motor.create_drive()
            state.drive = True

        return motor