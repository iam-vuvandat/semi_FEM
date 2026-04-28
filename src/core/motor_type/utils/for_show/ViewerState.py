import numpy as np
import pyvista as pv
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QTimer

from src.core.motor_type.utils.for_show._add_cylindrical_axes_static import _add_cylindrical_axes_static

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
        self.show_axes = True
        self.axes_scale = 1.0

        self.pl.enable_lightkit()
        
        dist = base_len * 3
        az_rad = np.radians(-142.2)
        el_rad = np.radians(28.3)
        cx = dist * np.cos(el_rad) * np.cos(az_rad)
        cy = dist * np.cos(el_rad) * np.sin(az_rad)
        cz = dist * np.sin(el_rad)
        self.pl.camera_position = [(cx, cy, cz), (0, 0, 0), (0, 0, 1)]
        
        self.pl.add_on_render_callback(lambda plotter: self.update_camera_info())

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self._update_limits()
        self.pos_i, self.pos_k = self.max_i // 2, self.max_k // 2

    @property
    def active_grid(self): 
        return self.grid_full if (self.use_symmetry and self.grid_full) else self.grid_sector
    
    @property
    def _actors(self): 
        return self.pl.renderer.actors

    def _update_limits(self):
        dims = self.dim_full if (self.use_symmetry and self.grid_full) else self.dim_sector
        self.max_i, self.max_j, self.max_k = dims
        self.pos_i = np.clip(self.pos_i, 0, self.max_i - 1)
        self.pos_j = np.clip(self.pos_j, 0, self.max_j - 1)
        self.pos_k = np.clip(self.pos_k, 0, self.max_k - 1)

    def resize_axes(self, sign):
        step = 0.1
        self.axes_scale = np.clip(self.axes_scale + sign * step, 0.1, 5.0)
        new_len = self.base_axes_len * self.axes_scale
        _add_cylindrical_axes_static(self.pl, new_len)
        self.update_static_visibility()

    def init_static_layers(self):
        if self.geometry_obj and self.geometry_obj.geometry:
            for idx, seg in enumerate(self.geometry_obj.geometry):
                if seg.mesh is None: continue
                mat = str(seg.material).lower()
                color = "#3498DB" 
                if "iron" in mat or "steel" in mat: color = "#B0B0B0" 
                elif "magnet" in mat: color = "#E74C3C"
                elif "copper" in mat or "coil" in mat: color = "#E67E22"
                elif "air" in mat: color = "#E0F7FA"
                op = 0.15 if "air" in mat else 1.0
                pv_mesh = pv.wrap(seg.mesh) if not isinstance(seg.mesh, pv.DataSet) else seg.mesh
                self.pl.add_mesh(pv_mesh, color=color, opacity=op, lighting=True, 
                            specular=0.1, ambient=0.4, diffuse=0.7, name=f"geo_full_{idx}")
                sector_mesh = pv_mesh.copy()
                if self.sym_factor > 1:
                    try:
                        theta_rad = np.radians(360.0 / self.sym_factor)
                        sector_mesh = sector_mesh.clip(normal=(0, -1, 0), origin=(0, 0, 0))
                        n_clip = (-np.sin(theta_rad), np.cos(theta_rad), 0)
                        sector_mesh = sector_mesh.clip(normal=n_clip, origin=(0, 0, 0))
                    except Exception:
                        pass
                self.pl.add_mesh(sector_mesh, color=color, opacity=op, lighting=True, 
                            specular=0.1, ambient=0.4, diffuse=0.7, name=f"geo_sec_{idx}")
        self._redraw_wireframe()
        self.update_static_visibility()

    def _redraw_wireframe(self):
        if "static_mesh_wire" in self._actors: self.pl.remove_actor("static_mesh_wire")
        self.pl.add_mesh(self.active_grid, style='wireframe', color='black', opacity=0.05, 
                    line_width=1, name="static_mesh_wire")
        if "static_mesh_wire" in self._actors:
            self._actors["static_mesh_wire"].SetVisibility(self.show_mesh_lines)

    def update_static_visibility(self):
        if self.geometry_obj:
            for idx in range(len(self.geometry_obj.geometry)):
                if f"geo_full_{idx}" in self._actors: 
                    self._actors[f"geo_full_{idx}"].SetVisibility(self.show_geometry and self.use_symmetry)
                if f"geo_sec_{idx}" in self._actors: 
                    self._actors[f"geo_sec_{idx}"].SetVisibility(self.show_geometry and not self.use_symmetry)
        if "static_mesh_wire" in self._actors: 
            self._actors["static_mesh_wire"].SetVisibility(self.show_mesh_lines)
        for n in ['axis_z', 'axis_r', 'axis_arc', 'axis_tip_th']:
            if n in self._actors: self._actors[n].SetVisibility(self.show_axes)
        if hasattr(self.pl, '_labels_actor') and self.pl._labels_actor:
            self.pl._labels_actor.SetVisibility(self.show_axes)
        self.pl.render()

    def toggle_geometry_btn(self, state):
        self.show_geometry = state
        if state: 
            self.bmap_mode = False
            if self.ref_act_bmap: self.ref_act_bmap.setChecked(False)
        self.update_static_visibility()
        self.render()

    def toggle_bmap_btn(self, state):
        if not self.has_results or self.total_frames == 0:
            self.bmap_mode = False
            if self.ref_act_bmap: self.ref_act_bmap.setChecked(False)
            return
        self.bmap_mode = state
        if state:
            self.show_geometry = False
            if self.ref_act_geo: self.ref_act_geo.setChecked(False)
            self.update_static_visibility()
        self.render()

    def toggle_symmetry_btn(self, state):
        if self.sym_factor <= 1: return
        self.use_symmetry = state
        self._update_limits()
        self._redraw_wireframe()
        self.update_static_visibility()
        self.render()

    def toggle_mesh_btn(self, s): self.show_mesh_lines = s; self.update_static_visibility()
    def toggle_axes_btn(self, s): self.show_axes = s; self.update_static_visibility()

    def _safe_remove(self, name):
        if name in self._actors: self.pl.remove_actor(name)
    def _safe_add(self, mesh, **kwargs):
        kwargs['reset_camera'] = False
        self.pl.add_mesh(mesh, **kwargs)

    def get_current_data(self):
        n_cells = self.active_grid.n_cells
        if not self.has_results or self.total_frames == 0:
            return np.zeros(n_cells, dtype=int), np.zeros(n_cells)
        el_lite = self.history[self.current_frame].flatten(order='F')
        b_sec, mat_sec = np.zeros(len(el_lite)), np.zeros(len(el_lite), dtype=int)
        for idx, el in enumerate(el_lite):
            if el is None: continue
            m = el.material.lower()
            if "iron" in m: mat_sec[idx] = 1
            elif "magnet" in m: 
                z_val = el.magnetization_direction[-1] if el.magnetization_direction is not None else 0
                mat_sec[idx] = 2 if z_val >= 0 else 4
            elif "coil" in m: mat_sec[idx] = 3
            if el.flux_density_average is not None: b_sec[idx] = el.flux_density_average[-1]
        if self.use_symmetry and self.sym_factor > 1:
            return np.tile(mat_sec, self.sym_factor), np.tile(b_sec, self.sym_factor)
        return mat_sec, b_sec

    def render(self):
        if self.show_geometry:
            self._safe_remove("dynamic_mesh")
            for mid in range(5): self._safe_remove(f"mat_{mid}")
            self.update_text_info(); self.pl.render(); return
        grid = self.active_grid
        mat_ids, b_vals = self.get_current_data()
        grid.cell_data["MatID"], grid.cell_data["FluxB"] = mat_ids, b_vals
        mask = np.zeros(grid.n_cells, dtype=bool)
        has_sel = self.show_i or self.show_j or self.show_k
        if not has_sel: mask[:] = True
        else:
            if self.show_i: mask |= (grid.cell_data["idx_i"] == self.pos_i)
            if self.show_j: mask |= (grid.cell_data["idx_j"] == self.pos_j)
            if self.show_k: mask |= (grid.cell_data["idx_k"] == self.pos_k)
        try: render_mesh = grid.extract_cells(mask)
        except Exception: render_mesh = pv.UnstructuredGrid()
        if render_mesh.n_cells == 0:
            self._safe_remove("dynamic_mesh")
            for mid in range(5): self._safe_remove(f"mat_{mid}")
            self.update_text_info(); self.pl.render(); return
        if self.bmap_mode:
            for mid in range(5): self._safe_remove(f"mat_{mid}")
            target = render_mesh if has_sel else render_mesh.threshold(0.1, scalars="MatID")
            if target.n_cells > 0:
                self._safe_add(target, scalars="FluxB", cmap="jet", clim=[0, 2.0],
                                lighting=False, scalar_bar_args=self.sargs, show_scalar_bar=True, name="dynamic_mesh")
            else: self._safe_remove("dynamic_mesh")
        else:
            self._safe_remove("dynamic_mesh")
            if self.pl.scalar_bars: self.pl.scalar_bars.clear()
            for mid, col in self.colors_net.items():
                try:
                    sub = render_mesh.threshold([mid, mid], scalars="MatID")
                    op = 1.0 if has_sel else (0.05 if mid == 0 else 1.0)
                    actual_col = "#B0B0B0" if mid == 1 else col
                    self._safe_add(sub, color=actual_col, opacity=op, lighting=True, 
                                   ambient=0.4, diffuse=0.7, specular=0.1,
                                   show_edges=True, edge_color="#333333", name=f"mat_{mid}")
                except Exception: self._safe_remove(f"mat_{mid}")
        self.update_text_info(); self.pl.render()

    def update_text_info(self):
        st = lambda s, p, m: f"ON [{p}/{m-1}]" if s else "OFF"
        frame_txt = "No Results (Unsolved)" if (not self.has_results or self.total_frames == 0) else f"{self.current_frame + 1} / {self.total_frames}"
        info_left = f"Frame: {frame_txt}\nSym: {'ON' if self.use_symmetry else 'OFF'}\n" \
                    f"R: {st(self.show_i, self.pos_i, self.max_i)}\n" \
                    f"Th: {st(self.show_j, self.pos_j, self.max_j)}\n" \
                    f"Z: {st(self.show_k, self.pos_k, self.max_k)}"
        self.pl.add_text(info_left, position="upper_left", font_size=9, name="info_text", color='black')
        total_elements = self.active_grid.n_cells 
        grid_dims = f"{self.max_i} x {self.max_j} x {self.max_k}"
        info_right = f"Total Elements: {total_elements}\nGrid: {grid_dims}"
        self.pl.add_text(info_right, position="upper_right", font_size=9, name="grid_info_text", color='black')
        self.update_camera_info()

    def update_camera_info(self):
        pos = np.array(self.pl.camera.position)
        focal = np.array(self.pl.camera.focal_point)
        vec = pos - focal
        az = np.degrees(np.arctan2(vec[1], vec[0]))
        xy_dist = np.sqrt(vec[0]**2 + vec[1]**2)
        el = np.degrees(np.arctan2(vec[2], xy_dist))
        current_angle = (round(az, 1), round(el, 1))
        if hasattr(self, '_last_cam_angle') and self._last_cam_angle == current_angle:
            return
        self._last_cam_angle = current_angle
        cam_text = f"Camera: Az {current_angle[0]:.1f}°, El {current_angle[1]:.1f}°"
        self.pl.add_text(cam_text, position="lower_right", font_size=8, name="camera_info", color='black')

    def next_frame(self): 
        if self.has_results and self.total_frames > 0:
            self.current_frame = (self.current_frame + 1) % self.total_frames
            self.render()
    def pre_frame(self): 
        if self.has_results and self.total_frames > 0:
            self.current_frame = (self.current_frame - 1) % self.total_frames
            self.render()
    def toggle_play(self): 
        if self.has_results and self.total_frames > 0:
            self.is_playing = not self.is_playing
            self.timer.start(100) if self.is_playing else self.timer.stop()
    
    def save_gif(self):
        if not self.has_results or self.total_frames == 0: return
        was = self.is_playing; self.timer.stop(); self.is_playing = False
        f, _ = QFileDialog.getSaveFileName(self.pl.app_window, "Save", "anim.gif", "GIF (*.gif)")
        if f:
            self.pl.open_gif(f)
            for i in range(self.total_frames): self.current_frame = i; self.render(); self.pl.write_frame()
            self.pl.close()
        if was: self.toggle_play()
        
    def save_screenshot_hd(self):
        old_bg = self.pl.background_color
        self.pl.set_background("white")
        f, _ = QFileDialog.getSaveFileName(self.pl.app_window, "Save HD Image", "motor_hd.png", "PNG (*.png)")
        if f: self.pl.screenshot(f, transparent_background=False, scale=4)
        self.pl.set_background(old_bg)