import numpy as np
import pyvista as pv
from pyvista.plotting.renderer import Renderer 
from pyvistaqt import BackgroundPlotter
import ctypes

# Import các utils đã tách
from src.core.motor_type.utils.for_show._process_grid_indices import _process_grid_indices
from src.core.motor_type.utils.for_show._add_cylindrical_axes_static import _add_cylindrical_axes_static
from src.core.motor_type.utils.for_show._build_full_grid import _build_full_grid
from src.core.motor_type.utils.for_show._setup_viewer_ui import _setup_viewer_ui
from src.core.motor_type.utils.for_show.ViewerState import ViewerState

# --- PATCH PYTHON 3.13 ---
_original_init = Renderer.__init__
def _patched_init(self, *args, **kwargs):
    _original_init(self, *args, **kwargs)
    if not hasattr(self, '_actors'):
        self._actors = getattr(self, 'actors', {})
Renderer.__init__ = _patched_init

# Tối ưu DPI
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception: pass


def show_motor(motor):
    # Thiết lập độ dày nét vẽ toàn cục (ví dụ: 0.5 là rất mảnh, 2.0 là dày)
    pv.global_theme.line_width = 1.0

    # 1. Kiểm tra thuộc tính
    motor.require('geometry')
    motor.require('mesh')
    
    # 2. Thu thập dữ liệu
    reluctance_network = getattr(motor, 'reluctance_network', None)
    geometry_obj = motor.geometry
    mesh_obj = motor.mesh
    
    has_results = reluctance_network is not None and hasattr(reluctance_network, 'list_elements_lite')
    history = reluctance_network.list_elements_lite if has_results else []

    # 3. Chuẩn bị lưới (Mesh)
    grid_sector = mesh_obj.to_pyvista_grid()
    dim_sector = _process_grid_indices(grid_sector)
    
    sym_factor = int(getattr(reluctance_network, 'symmetry_factor', 1)) if reluctance_network else 1
    grid_full, dim_full = _build_full_grid(grid_sector, dim_sector, sym_factor)
    
    # 4. Khởi tạo Plotter
    pl = BackgroundPlotter(title="Integrated Motor Viewer", window_size=(1600, 900))
    pl.set_background("#FFFFFF")
    pl.default_camera_tool_bar.hide()
    pl.saved_cameras_tool_bar.hide()
    
    base_len = np.max(mesh_obj.r_nodes) * 1.2 if (hasattr(mesh_obj, 'r_nodes') and len(mesh_obj.r_nodes) > 0) else 100
    _add_cylindrical_axes_static(pl, base_len)

    # 5. Cấu hình UI & Trạng thái
    colors_net = {0: "#444444", 1: "#1976D2", 2: "#FF3333", 3: "#FF9900", 4: "#FF3333"}
    sargs = dict(title="Flux Density (T)", title_font_size=20, label_font_size=16,
                 n_labels=6, fmt="%.2f", vertical=True, position_x=0.92, position_y=0.15,
                 height=0.7, width=0.04, color='black', shadow=False)

    state = ViewerState(
        pl=pl,
        history=history,
        geometry_obj=geometry_obj,
        grid_sector=grid_sector,
        grid_full=grid_full,
        dim_sector=dim_sector,
        dim_full=dim_full,
        sym_factor=sym_factor,
        base_len=base_len,
        has_results=has_results,
        colors_net=colors_net,
        sargs=sargs
    )
    
    state.init_static_layers()
    state.render()
    pl.reset_camera()

    # 6. Gắn UI Toolbar/Menu (Đã được định nghĩa ở file _setup_viewer_ui.py)
    _setup_viewer_ui(pl, state, sym_factor, has_results)

    # 7. Thực thi
    pl.show()
    pl.app.exec_()