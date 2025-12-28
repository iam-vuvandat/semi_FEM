import numpy as np
import pyvista as pv
from pyvistaqt import BackgroundPlotter
from PyQt5.QtWidgets import QAction, QStyle
from PyQt5.QtCore import QTimer
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

def show_reluctance_network(reluctance_network, use_symmetry_factor=True):
    history = reluctance_network.list_elements_lite
    if not history:
        return

    mesh_obj = reluctance_network.mesh
    grid_pv = mesh_obj.to_pyvista_grid()
    n_cells_sector = grid_pv.n_cells
    
    pl = BackgroundPlotter(title="Reluctance Network Animation", window_size=(1600, 900))
    pl.set_background("#FFFFFF")
    pl.add_axes(color='black')

    pl.default_camera_tool_bar.hide()
    pl.saved_cameras_tool_bar.hide()

    colors = {0: "#F0F0F0", 1: "#8B8888", 2: "#FF3333", 3: "#FF9900", 4: "#3366FF"}
    sargs = dict(
        title="Flux Density (T)", title_font_size=20, label_font_size=16,
        n_labels=6, fmt="%.2f", vertical=True, position_x=0.92, position_y=0.15,
        height=0.7, width=0.04, color='black', shadow=False
    )

    class ViewerState:
        def __init__(self):
            self.current_frame = 0
            self.total_frames = len(history)
            self.bmap_mode = False
            self.solid_mode = False
            self.is_playing = False
            self.timer = QTimer()
            self.timer.timeout.connect(self.next_frame)

        def get_current_data(self):
            elements_lite = history[self.current_frame].flatten(order='F')
            mat_ids = np.zeros(n_cells_sector, dtype=int)
            b_values = np.zeros(n_cells_sector, dtype=float)

            for idx, el in enumerate(elements_lite):
                if el is None: continue
                m_name = el.material.lower()
                if "iron" in m_name or "steel" in m_name: mat_ids[idx] = 1
                elif "magnet" in m_name:
                    z_val = el.magnetization_direction[-1] if el.magnetization_direction is not None else 0
                    mat_ids[idx] = 2 if z_val >= 0 else 4
                elif "coil" in m_name or "winding" in m_name: mat_ids[idx] = 3
                if el.flux_density_average is not None:
                    b_values[idx] = el.flux_density_average[-1]

            if use_symmetry_factor and hasattr(reluctance_network, 'symmetry_factor'):
                sym = int(reluctance_network.symmetry_factor)
                if sym > 1:
                    mat_ids = np.tile(mat_ids, sym)
                    b_values = np.tile(b_values, sym)
            return mat_ids, b_values

        def render(self):
            mat_ids, b_values = self.get_current_data()
            grid_pv.cell_data["MatID"] = mat_ids
            grid_pv.cell_data["FluxB"] = b_values
            opacity_val = 1.0 if self.solid_mode else 0.4
            
            if self.bmap_mode:
                for mid in range(5): pl.remove_actor(f"mat_{mid}")
                non_air = grid_pv.threshold(0.1, scalars="MatID", preference="cell")
                if non_air.n_cells > 0:
                    pl.add_mesh(non_air, scalars="FluxB", cmap="jet", clim=[0, 1.8],
                                opacity=opacity_val, show_edges=False, lighting=True,
                                scalar_bar_args=sargs, show_scalar_bar=True, name="bmap_mesh")
            else:
                pl.remove_actor("bmap_mesh")
                if len(pl.scalar_bars) > 0: pl.scalar_bars.clear()
                for mid, color in colors.items():
                    sub = grid_pv.threshold([mid, mid], scalars="MatID", preference="cell")
                    if sub.n_cells > 0:
                        op = 0.1 if mid == 0 else opacity_val
                        pl.add_mesh(sub, color=color, opacity=op, lighting=True,
                                    show_edges=self.solid_mode, edge_color="#222222", 
                                    name=f"mat_{mid}")
                    else:
                        pl.remove_actor(f"mat_{mid}")
            
            pl.add_text(f"Frame: {self.current_frame}/{self.total_frames-1}", 
                        position="upper_left", font_size=10, color="black", name="info_text")
            pl.render()

        def toggle_bmap(self, state):
            self.bmap_mode = state
            self.render()

        def toggle_solid(self, state):
            self.solid_mode = state
            self.render()

        def next_frame(self):
            self.current_frame = (self.current_frame + 1) % self.total_frames
            self.render()

        def pre_frame(self):
            self.current_frame = (self.current_frame - 1) % self.total_frames
            self.render()

        def toggle_play(self):
            self.is_playing = not self.is_playing
            if self.is_playing: self.timer.start(100)
            else: self.timer.stop()

    state = ViewerState()
    
    if use_symmetry_factor and hasattr(reluctance_network, 'symmetry_factor'):
        sym_factor = int(reluctance_network.symmetry_factor)
        if sym_factor > 1:
            angle_step = 360.0 / sym_factor
            segments = [grid_pv.rotate_z(i * angle_step) for i in range(sym_factor)]
            grid_pv = segments[0].merge(segments[1:]).clean(tolerance=1e-5)

    state.render()

    tb = pl.app_window.addToolBar("Simulation Controls")

    act_solid = QAction("Solid", pl.app_window)
    act_solid.setCheckable(True)
    act_solid.triggered.connect(state.toggle_solid)
    tb.addAction(act_solid)

    act_bmap = QAction("B-Map", pl.app_window)
    act_bmap.setCheckable(True)
    act_bmap.triggered.connect(state.toggle_bmap)
    tb.addAction(act_bmap)

    tb.addSeparator()

    act_pre = QAction(pl.app_window.style().standardIcon(QStyle.SP_MediaSkipBackward), "Pre", pl.app_window)
    act_pre.triggered.connect(state.pre_frame)
    tb.addAction(act_pre)

    act_play = QAction(pl.app_window.style().standardIcon(QStyle.SP_MediaPlay), "Play", pl.app_window)
    act_play.triggered.connect(state.toggle_play)
    tb.addAction(act_play)

    act_next = QAction(pl.app_window.style().standardIcon(QStyle.SP_MediaSkipForward), "Next", pl.app_window)
    act_next.triggered.connect(state.next_frame)
    tb.addAction(act_next)

    pl.show()
    pl.app.exec_()