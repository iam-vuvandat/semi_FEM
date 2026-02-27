import numpy as np
import pyvista as pv
from pyvistaqt import QtInteractor
from PyQt5.QtCore import QTimer

def display_reluctance_network(reluctance_network, plotter=None):
    if reluctance_network is None: return

    def _process_grid_indices(grid):
        if grid.n_points == 0: return 0, 0, 0
        centers = grid.cell_centers().points
        r = np.sqrt(centers[:, 0]**2 + centers[:, 1]**2)
        th = np.degrees(np.arctan2(centers[:, 1], centers[:, 0])); th[th < 0] += 360
        z = centers[:, 2]
        DEC = 4
        u_r, u_th, u_z = [np.unique(np.round(x, DEC)) for x in [r, th, z]]
        grid.cell_data["idx_i"] = np.searchsorted(u_r, np.round(r, DEC))
        grid.cell_data["idx_j"] = np.searchsorted(u_th, np.round(th, DEC))
        grid.cell_data["idx_k"] = np.searchsorted(u_z, np.round(z, DEC))
        return len(u_r), len(u_th), len(u_z)

    history = getattr(reluctance_network, 'list_elements_lite', [])
    grid_sector = reluctance_network.mesh.to_pyvista_grid()
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

    pl = plotter 

    class ViewerState:
        def __init__(self):
            self.current_frame = 0
            self.total_frames = len(history)
            self.is_playing = False
            self.bmap_mode = True
            self.use_symmetry = False
            
            self.show_i = self.show_j = self.show_k = False
            self.pos_i, self.pos_j, self.pos_k = dim_full[0]//2, 0, dim_full[2]//2
            self.max_i, self.max_j, self.max_k = dim_full

            self.timer = QTimer()
            self.timer.timeout.connect(self.next_frame)
            
            self.sargs = dict(
                title="Flux Density (T)", 
                title_font_size=14,
                label_font_size=12,
                n_labels=6, 
                fmt="%.2f", 
                vertical=True, 
                position_x=0.82,
                position_y=0.15, 
                height=0.7, 
                width=0.05, 
                color='black', 
                shadow=False
            )
            self.colors_net = {0: "#FFFFFF8E", 1: "#A5C5E5", 2: "#BC8E8E", 3: "#FF9900", 4: "#3366FF"}
            self.colors_hex = [
                "#0000ff", "#0049ff", "#0092ff", "#00dbff",
                "#00ffdb", "#00ff92", "#00ff49", "#00ff00",
                "#49ff00", "#92ff00", "#dbff00", "#ffdb00",
                "#ff9200", "#ff4900", "#ff0000"
            ]

        @property
        def active_grid(self): return grid_full if (self.use_symmetry and sym_factor > 1) else grid_sector

        def _update_limits(self):
            dims = dim_full if (self.use_symmetry and sym_factor > 1) else dim_sector
            self.max_i, self.max_j, self.max_k = dims
            self.pos_i = np.clip(self.pos_i, 0, self.max_i - 1)
            self.pos_j = np.clip(self.pos_j, 0, self.max_j - 1)
            self.pos_k = np.clip(self.pos_k, 0, self.max_k - 1)

        def _safe_remove(self, name):
            if name in pl.renderer.actors: pl.remove_actor(name)

        def get_frame_data(self):
            if not history: return np.zeros(self.active_grid.n_cells), np.zeros(self.active_grid.n_cells)
            el_lite = history[self.current_frame].flatten(order='F')
            b_sec = np.array([el.flux_density_average[-1] if (el and el.flux_density_average is not None) else 0.0 for el in el_lite])
            mat_sec = np.zeros(len(el_lite), dtype=int)
            for idx, el in enumerate(el_lite):
                if not el: continue
                m = el.material.lower()
                if "iron" in m: mat_sec[idx] = 1
                elif "magnet" in m:
                    z = el.magnetization_direction[-1] if el.magnetization_direction is not None else 0
                    mat_sec[idx] = 2 if z >= 0 else 4
                elif "coil" in m: mat_sec[idx] = 3
            
            if self.use_symmetry and sym_factor > 1:
                return np.tile(mat_sec, sym_factor), np.tile(b_sec, sym_factor)
            return mat_sec, b_sec

        def render(self):
            grid = self.active_grid
            mat_ids, b_vals = self.get_frame_data()
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
            elif self.bmap_mode:
                for mid in range(5): self._safe_remove(f"mat_{mid}")
                target = render_mesh if has_sel else render_mesh.threshold(0.1, scalars="MatID")
                
                pl.add_mesh(target, scalars="FluxB", cmap=self.colors_hex, clim=[0, 2.0], 
                            name="dynamic_mesh", show_scalar_bar=False, reset_camera=False, lighting=False)
                
                if not pl.scalar_bars:
                    pl.add_scalar_bar(**self.sargs)
            else:
                self._safe_remove("dynamic_mesh")
                if pl.scalar_bars: pl.scalar_bars.clear()
                for mid, col in self.colors_net.items():
                    try:
                        sub = render_mesh.threshold([mid, mid], scalars="MatID")
                        op = 1.0 if has_sel else (0.05 if mid == 0 else 1.0)
                        pl.add_mesh(sub, color=col, opacity=op, show_edges=True, 
                                    edge_color="#333333", name=f"mat_{mid}", reset_camera=False)
                    except: self._safe_remove(f"mat_{mid}")
            
            st = lambda s, p, m: f"ON [{p}/{m-1}]" if s else "OFF"
            info = f"Frame: {self.current_frame} | Sym: {'ON' if self.use_symmetry else 'OFF'}\n" \
                   f"R: {st(self.show_i, self.pos_i, self.max_i)} | Th: {st(self.show_j, self.pos_j, self.max_j)} | Z: {st(self.show_k, self.pos_k, self.max_k)}"
            pl.add_text(info, position="upper_left", font_size=9, name="info_text")
            pl.render()

        def next_frame(self):
            self.current_frame = (self.current_frame + 1) % self.total_frames
            self.render()

    pl.viewer_state = ViewerState()
    pl.viewer_state.render()
    pl.reset_camera()
    pl.set_focus([0, 0, 0])
    return pl.viewer_state