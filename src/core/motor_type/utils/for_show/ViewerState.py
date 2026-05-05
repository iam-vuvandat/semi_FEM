import numpy as np
import pyvista as pv
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QTimer

from src.core.motor_type.utils.for_show.for_viewer_state.save_screenshot_hd import save_screenshot_hd
from src.core.motor_type.utils.for_show.for_viewer_state.save_gif import save_gif
from src.core.motor_type.utils.for_show.for_viewer_state._rescale_camera import _rescale_camera
from src.core.motor_type.utils.for_show.for_viewer_state._update_limits import _update_limits
from src.core.motor_type.utils.for_show.for_viewer_state.resize_axes import resize_axes
from src.core.motor_type.utils.for_show.for_viewer_state.init_static_layers import init_static_layers
from src.core.motor_type.utils.for_show.for_viewer_state._redraw_wireframe import _redraw_wireframe
from src.core.motor_type.utils.for_show.for_viewer_state.update_static_visibility import update_static_visibility
from src.core.motor_type.utils.for_show.for_viewer_state.toggle_geometry_btn import toggle_geometry_btn
from src.core.motor_type.utils.for_show.for_viewer_state.toggle_bmap_btn import toggle_bmap_btn
from src.core.motor_type.utils.for_show.for_viewer_state.toggle_symmetry_btn import toggle_symmetry_btn
from src.core.motor_type.utils.for_show.for_viewer_state.toggle_mesh_btn import toggle_mesh_btn
from src.core.motor_type.utils.for_show.for_viewer_state.toggle_axes_btn import toggle_axes_btn
from src.core.motor_type.utils.for_show.for_viewer_state._safe_remove import _safe_remove
from src.core.motor_type.utils.for_show.for_viewer_state._safe_add import _safe_add
from src.core.motor_type.utils.for_show.for_viewer_state.get_current_data import get_current_data
from src.core.motor_type.utils.for_show.for_viewer_state.render import render
from src.core.motor_type.utils.for_show.for_viewer_state.update_text_info import update_text_info
from src.core.motor_type.utils.for_show.for_viewer_state.update_camera_info import update_camera_info
from src.core.motor_type.utils.for_show.for_viewer_state.next_frame import next_frame
from src.core.motor_type.utils.for_show.for_viewer_state.pre_frame import pre_frame
from src.core.motor_type.utils.for_show.for_viewer_state.toggle_play import toggle_play
from src.core.motor_type.utils.for_show.for_viewer_state.view_iso import view_iso

class ViewerState:
    def __init__(self, pl, history, geometry_obj, grid_sector, grid_full, 
                 dim_sector, dim_full, sym_factor, base_len, has_results, 
                 colors_net, sargs):
        self.pl = pl
        self.history = history
        self.geometry_obj = geometry_obj
        self.grid_sector = grid_sector
        self.grid_full = grid_full
        self.dim_sector = dim_sector
        self.dim_full = dim_full
        self.sym_factor = sym_factor
        self.base_axes_len = base_len
        self.has_results = has_results
        self.colors_net = colors_net
        self.sargs = sargs

        self.ref_act_geo = None
        self.ref_act_bmap = None
        
        self.total_frames = len(self.history) if self.history is not None else 0
        self.current_frame = 0
        self.is_playing = False
        
        self.bmap_mode = (self.total_frames > 0)
        self.show_geometry = (not self.bmap_mode)
        
        self.use_symmetry = False       
        self.show_i = False             
        self.show_j = False             
        self.show_k = False             
        
        self.pos_i, self.pos_j, self.pos_k = 0, 0, 0
        self.show_mesh_lines = False
        self.show_axes = False
        self.axes_scale = 1.0

        self._last_cam_pos = None

        self.pl.enable_lightkit()
        
        try:
            # Khởi tạo khối lập phương chuyển góc nhìn
            cam_widget = self.pl.add_camera_orientation_widget()
            
            # Can thiệp vào lớp hiển thị (Representation) của VTK để neo nó xuống góc dưới, bên trái
            if hasattr(cam_widget, 'GetRepresentation'):
                cam_widget.GetRepresentation().AnchorToLowerLeft()
                
        except Exception:
            # Fallback an toàn nếu thư viện VTK phiên bản cũ không hỗ trợ
            self.pl.add_axes(interactive=True)
        
        default_view_scale = (0.494, -0.714, 0.493)
        self.dist_factor = base_len * 3
        cx = default_view_scale[0] * self.dist_factor
        cy = default_view_scale[1] * self.dist_factor
        cz = default_view_scale[2] * self.dist_factor
        self.pl.camera_position = [(cx, cy, cz), (0, 0, 0), (0, 0, 1)]
        
        self.pl.add_on_render_callback(lambda plotter: self.update_camera_info())

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self._update_limits()
        self.pos_i, self.pos_k = self.max_i // 2, self.max_k // 2

    def view_x(self):
        self.pl.view_yz()
        self._rescale_camera()

    def view_y(self):
        self.pl.view_xz()
        self._rescale_camera()

    def view_z(self):
        self.pl.view_xy()
        self._rescale_camera()

    def view_iso(self):
        view_iso(self)

    def _rescale_camera(self):
        _rescale_camera(self)

    @property
    def active_grid(self): 
        return self.grid_full if (self.use_symmetry and self.grid_full) else self.grid_sector
    
    @property
    def _actors(self): 
        return self.pl.renderer.actors

    def _update_limits(self):
        _update_limits(self)

    def resize_axes(self, sign):
        resize_axes(self, sign)

    def init_static_layers(self):
        init_static_layers(self)

    def _redraw_wireframe(self):
        _redraw_wireframe(self)

    def update_static_visibility(self):
        update_static_visibility(self)

    def toggle_geometry_btn(self, state):
        toggle_geometry_btn(self, state)

    def toggle_bmap_btn(self, state):
        toggle_bmap_btn(self, state)

    def toggle_symmetry_btn(self, state):
        toggle_symmetry_btn(self, state)

    def toggle_mesh_btn(self, s): 
        toggle_mesh_btn(self, s)

    def toggle_axes_btn(self, s): 
        toggle_axes_btn(self, s)

    def _safe_remove(self, name):
        _safe_remove(self, name)

    def _safe_add(self, mesh, **kwargs):
        _safe_add(self, mesh, **kwargs)

    def get_current_data(self):
        return get_current_data(self)

    def render(self):
        render(self)

    def update_text_info(self):
        update_text_info(self)

    def update_camera_info(self):
        update_camera_info(self)

    def next_frame(self): 
        next_frame(self)
            
    def pre_frame(self): 
        pre_frame(self)
            
    def toggle_play(self): 
        toggle_play(self)
    
    def save_gif(self):
        save_gif(self)
        
    def save_screenshot_hd(self):
        save_screenshot_hd(self)