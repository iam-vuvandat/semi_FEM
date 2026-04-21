import numpy as np
import pyvista as pv
from pyvista.plotting.renderer import Renderer 
from pyvistaqt import BackgroundPlotter
from PyQt5.QtWidgets import QAction, QStyle, QWidget, QFileDialog, QMenu
from PyQt5.QtCore import QTimer
import ctypes


from src.core.motor_type.utils.for_show._process_grid_indices import _process_grid_indices
from src.core.motor_type.utils.for_show._add_cylindrical_axes_static import _add_cylindrical_axes_static


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
    motor.require('geometry')
    motor.require('mesh')
    reluctance_network = motor.reluctance_network
    geometry_obj = motor.geometry
    history = reluctance_network.list_elements_lite
    if not history: return

    mesh_obj = reluctance_network.mesh
    grid_sector = mesh_obj.to_pyvista_grid()
    dim_sector = _process_grid_indices(grid_sector)
    
    sym_factor = int(getattr(reluctance_network, 'symmetry_factor', 1))
    grid_full = None
    dim_full = dim_sector
    
    if sym_factor > 1:
        step = 360.0 / sym_factor
        segments = [grid_sector.rotate_z(i * step) for i in range(sym_factor)]
        grid_full = segments[0].merge(segments[1:]).clean(tolerance=1e-5)
        dim_full = _process_grid_indices(grid_full)
    else:
        grid_full = grid_sector

    pl = BackgroundPlotter(title="Integrated Motor Viewer", window_size=(1600, 900))
    pl.set_background("#FFFFFF")
    
    base_len = np.max(mesh_obj.r_nodes) * 1.2 if len(mesh_obj.r_nodes) > 0 else 100
    _add_cylindrical_axes_static(pl, base_len)
    
    pl.default_camera_tool_bar.hide()
    pl.saved_cameras_tool_bar.hide()

    colors_net = {0: "#444444", 1: "#1976D2", 2: "#FF3333", 3: "#FF9900", 4: "#3366FF"}
    sargs = dict(title="Flux Density (T)", title_font_size=20, label_font_size=16,
                 n_labels=6, fmt="%.2f", vertical=True, position_x=0.92, position_y=0.15,
                 height=0.7, width=0.04, color='black', shadow=False)
    
    class ViewerState:
        def __init__(self):
            self.ref_act_geo = None
            self.ref_act_bmap = None
            
            self.current_frame = 0
            self.total_frames = len(history)
            self.is_playing = False
            
            # --- KHỞI TẠO THEO YÊU CẦU ---
            self.bmap_mode = True           # Bắt đầu với B-Map
            self.show_geometry = False      # Tắt Geometry khi xem B-Map
            self.use_symmetry = False       # Symmetry mặc định OFF
            self.show_i = False             # Tắt xem lớp R
            self.show_j = False             # Tắt xem lớp Th
            self.show_k = False             # Tắt xem lớp Z
            
            self.pos_i, self.pos_j, self.pos_k = 0, 0, 0
            self.show_mesh_lines = False
            self.show_axes = True
            self.axes_scale = 1.0
            self.base_axes_len = base_len

            self.timer = QTimer()
            self.timer.timeout.connect(self.next_frame)
            self._update_limits()
            self.pos_i, self.pos_k = self.max_i // 2, self.max_k // 2

        @property
        def active_grid(self): return grid_full if (self.use_symmetry and grid_full) else grid_sector
        @property
        def _actors(self): return pl.renderer.actors

        def _update_limits(self):
            dims = dim_full if (self.use_symmetry and grid_full) else dim_sector
            self.max_i, self.max_j, self.max_k = dims
            self.pos_i = np.clip(self.pos_i, 0, self.max_i - 1)
            self.pos_j = np.clip(self.pos_j, 0, self.max_j - 1)
            self.pos_k = np.clip(self.pos_k, 0, self.max_k - 1)

        def resize_axes(self, sign):
            step = 0.1
            self.axes_scale = np.clip(self.axes_scale + sign * step, 0.1, 5.0)
            new_len = self.base_axes_len * self.axes_scale
            _add_cylindrical_axes_static(pl, new_len)
            self.update_static_visibility()

        def init_static_layers(self):
            if geometry_obj and geometry_obj.geometry:
                for idx, seg in enumerate(geometry_obj.geometry):
                    if seg.mesh is None: continue
                    mat = str(seg.material).lower()
                    color = "#3498DB"
                    if "iron" in mat or "steel" in mat: color = "#1976D2"
                    elif "magnet" in mat: color = "#E74C3C"
                    elif "copper" in mat or "coil" in mat: color = "#E67E22"
                    elif "air" in mat: color = "#E0F7FA"
                    op = 0.15 if "air" in mat else 1.0
                    pl.add_mesh(seg.mesh, color=color, opacity=op, lighting=True, 
                                specular=0.0, ambient=0.4, name=f"geo_{idx}")
            self._redraw_wireframe()
            self.update_static_visibility()

        def _redraw_wireframe(self):
            if "static_mesh_wire" in self._actors: pl.remove_actor("static_mesh_wire")
            pl.add_mesh(self.active_grid, style='wireframe', color='black', opacity=0.1, 
                        line_width=1, name="static_mesh_wire")
            if "static_mesh_wire" in self._actors:
                self._actors["static_mesh_wire"].SetVisibility(self.show_mesh_lines)

        def update_static_visibility(self):
            if geometry_obj:
                for idx in range(len(geometry_obj.geometry)):
                    if f"geo_{idx}" in self._actors: 
                        self._actors[f"geo_{idx}"].SetVisibility(self.show_geometry)
            if "static_mesh_wire" in self._actors: 
                self._actors["static_mesh_wire"].SetVisibility(self.show_mesh_lines)
            for n in ['axis_z', 'axis_r', 'axis_arc', 'axis_tip_th']:
                if n in self._actors: self._actors[n].SetVisibility(self.show_axes)
            if hasattr(pl, '_labels_actor') and pl._labels_actor:
                pl._labels_actor.SetVisibility(self.show_axes)
            pl.render()

        def toggle_geometry_btn(self, state):
            self.show_geometry = state
            if state: 
                self.bmap_mode = False
                if self.ref_act_bmap: self.ref_act_bmap.setChecked(False)
            self.update_static_visibility()
            self.render()

        def toggle_bmap_btn(self, state):
            self.bmap_mode = state
            if state:
                self.show_geometry = False
                if self.ref_act_geo: self.ref_act_geo.setChecked(False)
                self.update_static_visibility()
            self.render()

        def toggle_symmetry_btn(self, state):
            if sym_factor <= 1: return
            self.use_symmetry = state
            self._update_limits()
            self._redraw_wireframe()
            self.render()

        def toggle_mesh_btn(self, s): self.show_mesh_lines = s; self.update_static_visibility()
        def toggle_axes_btn(self, s): self.show_axes = s; self.update_static_visibility()

        def _safe_remove(self, name):
            if name in self._actors: pl.remove_actor(name)
        def _safe_add(self, mesh, **kwargs):
            kwargs['reset_camera'] = False
            pl.add_mesh(mesh, **kwargs)

        def get_current_data(self):
            el_lite = history[self.current_frame].flatten(order='F')
            b_sec = np.zeros(len(el_lite))
            mat_sec = np.zeros(len(el_lite), dtype=int)
            for idx, el in enumerate(el_lite):
                if el is None: continue
                m = el.material.lower()
                if "iron" in m: mat_sec[idx] = 1
                elif "magnet" in m: 
                    z_val = 0
                    if el.magnetization_direction is not None: z_val = el.magnetization_direction[-1]
                    mat_sec[idx] = 2 if z_val >= 0 else 4
                elif "coil" in m: mat_sec[idx] = 3
                if el.flux_density_average is not None: b_sec[idx] = el.flux_density_average[-1]
            if self.use_symmetry and sym_factor > 1:
                return np.tile(mat_sec, sym_factor), np.tile(b_sec, sym_factor)
            return mat_sec, b_sec

        def render(self):
            if self.show_geometry:
                self._safe_remove("dynamic_mesh")
                for mid in range(5): self._safe_remove(f"mat_{mid}")
                pl.render()
                return
            grid = self.active_grid
            mat_ids, b_vals = self.get_current_data()
            grid.cell_data["MatID"] = mat_ids
            grid.cell_data["FluxB"] = b_vals
            mask = np.zeros(grid.n_cells, dtype=bool)
            has_sel = self.show_i or self.show_j or self.show_k
            if not has_sel: mask[:] = True
            else:
                if self.show_i: mask |= (grid.cell_data["idx_i"] == self.pos_i)
                if self.show_j: mask |= (grid.cell_data["idx_j"] == self.pos_j)
                if self.show_k: mask |= (grid.cell_data["idx_k"] == self.pos_k)
            render_mesh = grid.extract_cells(mask)
            if render_mesh.n_cells == 0:
                self._safe_remove("dynamic_mesh")
                for mid in range(5): self._safe_remove(f"mat_{mid}")
                self.update_text_info()
                pl.render()
                return
            if self.bmap_mode:
                for mid in range(5): self._safe_remove(f"mat_{mid}")
                target = render_mesh if has_sel else render_mesh.threshold(0.1, scalars="MatID")
                if target.n_cells > 0:
                    self._safe_add(target, scalars="FluxB", cmap="jet", clim=[0, 2.0],
                                    lighting=False, scalar_bar_args=sargs, show_scalar_bar=True, name="dynamic_mesh")
                else: self._safe_remove("dynamic_mesh")
            else:
                self._safe_remove("dynamic_mesh")
                if pl.scalar_bars: pl.scalar_bars.clear()
                for mid, col in colors_net.items():
                    try:
                        sub = render_mesh.threshold([mid, mid], scalars="MatID")
                        op = 1.0 if has_sel else (0.05 if mid == 0 else 1.0)
                        self._safe_add(sub, color=col, opacity=op, lighting=True,
                                        show_edges=True, edge_color="#333333", name=f"mat_{mid}")
                    except: self._safe_remove(f"mat_{mid}")
            self.update_text_info()
            pl.render()

        def update_text_info(self):
            st = lambda s, p, m: f"ON [{p}/{m-1}]" if s else "OFF"
            info = f"Frame: {self.current_frame}\nSym: {'ON' if self.use_symmetry else 'OFF'}\n" \
                   f"R: {st(self.show_i, self.pos_i, self.max_i)}\n" \
                   f"Th: {st(self.show_j, self.pos_j, self.max_j)}\n" \
                   f"Z: {st(self.show_k, self.pos_k, self.max_k)}"
            pl.add_text(info, position="upper_left", font_size=9, name="info_text")

        def next_frame(self): self.current_frame = (self.current_frame + 1) % self.total_frames; self.render()
        def pre_frame(self): self.current_frame = (self.current_frame - 1) % self.total_frames; self.render()
        def toggle_play(self): self.is_playing = not self.is_playing; self.timer.start(100) if self.is_playing else self.timer.stop()
        def save_gif(self):
            was = self.is_playing; self.timer.stop(); self.is_playing = False
            f, _ = QFileDialog.getSaveFileName(pl.app_window, "Save", "anim.gif", "GIF (*.gif)")
            if f:
                pl.open_gif(f)
                for i in range(self.total_frames): self.current_frame = i; self.render(); pl.write_frame()
                pl.close()
            if was: self.toggle_play()
        def save_screenshot_hd(self):
            old_bg = pl.background_color
            pl.set_background("white")
            f, _ = QFileDialog.getSaveFileName(pl.app_window, "Save HD Image", "motor_hd.png", "PNG (*.png)")
            if f: pl.screenshot(f, transparent_background=False, scale=4); print(f"Saved to {f}")
            pl.set_background(old_bg)

    state = ViewerState()
    state.init_static_layers()
    state.render()
    pl.reset_camera()

    menubar = pl.app_window.menuBar()
    view_menu = None
    for action in menubar.actions():
        if "View" in action.text():
            view_menu = action.menu()
            break
    
    if view_menu:
        view_menu.clear() 
        
        # Geometry: Mặc định False
        act_geo = QAction("Show Geometry", pl.app_window); act_geo.setCheckable(True); act_geo.setChecked(False)
        act_geo.triggered.connect(state.toggle_geometry_btn); view_menu.addAction(act_geo)
        state.ref_act_geo = act_geo
        
        act_mesh = QAction("Show Mesh Wireframe", pl.app_window); act_mesh.setCheckable(True)
        act_mesh.triggered.connect(state.toggle_mesh_btn); view_menu.addAction(act_mesh)
        
        act_axes = QAction("Show Custom Axes", pl.app_window); act_axes.setCheckable(True); act_axes.setChecked(True)
        act_axes.triggered.connect(state.toggle_axes_btn); view_menu.addAction(act_axes)
        
        if sym_factor > 1:
            # Symmetry: Mặc định False
            act_sym = QAction("Enable Symmetry", pl.app_window); act_sym.setCheckable(True); act_sym.setChecked(False)
            act_sym.triggered.connect(state.toggle_symmetry_btn); view_menu.addAction(act_sym)
            
        # B-Map: Mặc định True
        act_bmap = QAction("Show B-Map (Flux)", pl.app_window); act_bmap.setCheckable(True); act_bmap.setChecked(True)
        act_bmap.triggered.connect(state.toggle_bmap_btn); view_menu.addAction(act_bmap)
        state.ref_act_bmap = act_bmap

        view_menu.addSeparator()
        scale_menu = view_menu.addMenu("Scale Axes")
        act_inc = QAction("Increase Size (+)", pl.app_window); act_inc.triggered.connect(lambda: state.resize_axes(1)); scale_menu.addAction(act_inc)
        act_dec = QAction("Decrease Size (-)", pl.app_window); act_dec.triggered.connect(lambda: state.resize_axes(-1)); scale_menu.addAction(act_dec)
        view_menu.addSeparator()
        act_hd = QAction("Screenshot HD", pl.app_window); act_hd.triggered.connect(state.save_screenshot_hd); view_menu.addAction(act_hd)

    tb = pl.app_window.addToolBar("Playback & Slicing")
    def add_slice(label, attr_show, attr_pos, check=False):
        a = QAction(label, pl.app_window); a.setCheckable(True); a.setChecked(check)
        a.triggered.connect(lambda s: (setattr(state, attr_show, s), state.render()))
        tb.addAction(a)
        l_attr = f"max_{attr_pos.split('_')[1]}"
        dec = QAction("-", pl.app_window); dec.triggered.connect(lambda: (setattr(state, attr_pos, np.clip(getattr(state, attr_pos)-1, 0, getattr(state, l_attr)-1)), state.render())); tb.addAction(dec)
        inc = QAction("+", pl.app_window); inc.triggered.connect(lambda: (setattr(state, attr_pos, np.clip(getattr(state, attr_pos)+1, 0, getattr(state, l_attr)-1)), state.render())); tb.addAction(inc)
        tb.addWidget(QWidget())

    # Tất cả các lớp (R, Th, Z) mặc định là False để xem Panorama
    add_slice("R", 'show_i', 'pos_i', False)
    add_slice("Th", 'show_j', 'pos_j', False)
    add_slice("Z", 'show_k', 'pos_k', False)
    
    tb.addSeparator()
    act_play = QAction(pl.app.style().standardIcon(QStyle.SP_MediaPlay), "", pl.app_window); act_play.triggered.connect(state.toggle_play); tb.addAction(act_play)
    act_gif = QAction("GIF", pl.app_window); act_gif.triggered.connect(state.save_gif); tb.addAction(act_gif)

    pl.show()
    pl.app.exec_()