from types import SimpleNamespace

class MotorStateManager:
    def __init__(self):
        self.ready_state = SimpleNamespace(
            material_database = False,
            winding_data      = False,
            mechanical        = False,
            geometry          = False,
            calculation_data  = False,
            mesh              = False,
            reluctance_network = False,
            drive             = False
        )
        
        self._order = [
            "material_database", "winding_data", "mechanical", 
            "geometry", "calculation_data", "mesh", 
            "reluctance_network", "drive"
        ]
        
        self._root_components = ["material_database", "winding_data"]

        self._reload_map = {
            "material_database": "reload_material",
            "winding_data": "reload_winding",
            "mechanical": "reload_mechanical",
            "geometry": "reload_geometry",
            "calculation_data": "reload_calculation_data",
            "mesh": "reload_mesh",
            "reluctance_network": "reload_reluctance_network",
            "drive": "reload_drive"
        }

    def just_changed(self, component_name):
        if component_name == "geometry" or component_name in self._root_components:
            for item in self._order:
                setattr(self.ready_state, item, False)
        else:
            found = False
            for item in self._order:
                if item == component_name:
                    found = True
                if found:
                    setattr(self.ready_state, item, False)

    def require(self, motor, component_name, callback=None):
        for item in self._order:
            if not getattr(self.ready_state, item):
                arg_name = self._reload_map[item]
                self.reload(motor, callback=callback, **{arg_name: True})
            
            if item == component_name:
                break

    def reload(self, motor, callback=None, **kwargs):
        state = self.ready_state

        def send_status(msg):
            if callback: callback(msg)

        if kwargs.get('reload_material'):
            send_status("Initializing material database...")
            motor.create_material_database()
            state.material_database = True

        if kwargs.get('reload_winding'):
            send_status("Generating motor winding analysis...")
            motor.create_winding()
            state.winding_data = True

        if kwargs.get('reload_mechanical'):
            send_status("Configuring mechanical properties...")
            motor.create_mechanical()
            state.mechanical = True

        if kwargs.get('reload_geometry'):
            send_status("Creating motor geometry...")
            motor.create_geometry()
            state.geometry = True

        if kwargs.get('reload_calculation_data'):
            send_status("Updating calculation parameters...")
            motor.create_calculation_data() # Đã thêm dòng này để đồng bộ
            state.calculation_data = True

        if kwargs.get('reload_mesh'):
            send_status("Generating adaptive mesh...")
            motor.create_adaptive_mesh()
            state.mesh = True

        if kwargs.get('reload_reluctance_network'):
            send_status("Building Reluctance Network model...")
            motor.create_reluctance_network(callback=callback)
            state.reluctance_network = True

        if kwargs.get('reload_drive'):
            send_status("Applying drive excitation...")
            motor.create_drive()
            state.drive = True

        return motor


 