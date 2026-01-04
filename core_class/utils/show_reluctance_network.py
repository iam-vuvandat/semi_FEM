import numpy as np
import pyvista as pv
from pyvistaqt import BackgroundPlotter
from PyQt5.QtWidgets import QAction, QStyle, QWidget, QLabel
from PyQt5.QtCore import QTimer
import ctypes

# Tối ưu hiển thị cho màn hình Surface (High DPI)
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

    # --- 1. CHUẨN BỊ DATA & LƯỚI ---
    mesh_obj = reluctance_network.mesh
    grid_pv = mesh_obj.to_pyvista_grid()
    
    # Xử lý đối xứng
    if use_symmetry_factor and hasattr(reluctance_network, 'symmetry_factor'):
        sym_factor = int(reluctance_network.symmetry_factor)
        if sym_factor > 1:
            angle_step = 360.0 / sym_factor
            segments = [grid_pv.rotate_z(i * angle_step) for i in range(sym_factor)]
            grid_pv = segments[0].merge(segments[1:]).clean(tolerance=1e-5)
    
    # --- 2. TỰ ĐỘNG PHÁT HIỆN LỚP (DISCRETE LAYERS) ---
    centers = grid_pv.cell_centers().points
    
    r_raw = np.sqrt(centers[:, 0]**2 + centers[:, 1]**2)
    theta_raw = np.degrees(np.arctan2(centers[:, 1], centers[:, 0]))
    theta_raw[theta_raw < 0] += 360
    theta_raw = np.round(theta_raw, 2) 
    z_raw = centers[:, 2]

    DECIMALS = 4
    u_r = np.unique(np.round(r_raw, DECIMALS))
    u_th = np.unique(np.round(theta_raw, DECIMALS))
    u_z = np.unique(np.round(z_raw, DECIMALS))

    N_I, N_J, N_K = len(u_r), len(u_th), len(u_z)
    print(f"Detected Mesh Layers: R={N_I}, Theta={N_J}, Z={N_K}")

    grid_pv.cell_data["idx_i"] = np.searchsorted(u_r, np.round(r_raw, DECIMALS))
    grid_pv.cell_data["idx_j"] = np.searchsorted(u_th, np.round(theta_raw, DECIMALS))
    grid_pv.cell_data["idx_k"] = np.searchsorted(u_z, np.round(z_raw, DECIMALS))

    # --- 3. PLOTTER ---
    pl = BackgroundPlotter(title="Reluctance Network - Production Version", window_size=(1600, 900))
    pl.set_background("#FFFFFF")
    pl.add_axes()
    pl.default_camera_tool_bar.hide()
    pl.saved_cameras_tool_bar.hide()

    colors = {0: "#444444", 1: "#E0E0E0", 2: "#FF3333", 3: "#FF9900", 4: "#3366FF"}
    sargs = dict(
        title="Flux Density (T)", title_font_size=20, label_font_size=16,
        n_labels=6, fmt="%.2f", vertical=True, position_x=0.92, position_y=0.15,
        height=0.7, width=0.04, color='black', shadow=False
    )

    class ViewerState:
        def __init__(self):
            self.current_frame = 0
            self.total_frames = len(history)
            self.is_playing = False
            self.bmap_mode = False 
            
            self.pos_i = N_I // 2
            self.pos_j = 0
            self.pos_k = N_K // 2

            self.show_i = False 
            self.show_j = False
            self.show_k = True 
            
            self.timer = QTimer()
            self.timer.timeout.connect(self.next_frame)

        def get_current_data(self):
            elements_lite = history[self.current_frame].flatten(order='F')
            b_sector = np.zeros(len(elements_lite), dtype=float)
            mat_sector = np.zeros(len(elements_lite), dtype=int)
            
            for idx, el in enumerate(elements_lite):
                if el is None: continue
                m_name = el.material.lower()
                if "iron" in m_name or "steel" in m_name: mat_sector[idx] = 1
                elif "magnet" in m_name:
                    z_val = el.magnetization_direction[-1] if el.magnetization_direction is not None else 0
                    mat_sector[idx] = 2 if z_val >= 0 else 4
                elif "coil" in m_name: mat_sector[idx] = 3
                if el.flux_density_average is not None:
                    b_sector[idx] = el.flux_density_average[-1]

            if use_symmetry_factor and hasattr(reluctance_network, 'symmetry_factor'):
                sym = int(reluctance_network.symmetry_factor)
                if sym > 1:
                    return np.tile(mat_sector, sym), np.tile(b_sector, sym)
            return mat_sector, b_sector
        
        # --- CÁC HÀM WRAPPER AN TOÀN (BỎ QUA LỖI) ---
        def safe_remove(self, name):
            try:
                if name in pl.actors: 
                    pl.remove_actor(name)
            except Exception: 
                pass # Chấp nhận lỗi để chạy tiếp

        def safe_add_mesh(self, mesh, **kwargs):
            try:
                # Ép buộc reset_camera=False để giữ zoom
                kwargs['reset_camera'] = False
                pl.add_mesh(mesh, **kwargs)
            except Exception:
                pass # Chấp nhận lỗi, PyVista sẽ tự xử lý ngầm

        def render(self):
            mat_ids, b_values = self.get_current_data()
            grid_pv.cell_data["MatID"] = mat_ids
            grid_pv.cell_data["FluxB"] = b_values
            
            has_selection = self.show_i or self.show_j or self.show_k
            
            mask_total = np.zeros(grid_pv.n_cells, dtype=bool)
            if self.show_i: mask_total |= (grid_pv.cell_data["idx_i"] == self.pos_i)
            if self.show_j: mask_total |= (grid_pv.cell_data["idx_j"] == self.pos_j)
            if self.show_k: mask_total |= (grid_pv.cell_data["idx_k"] == self.pos_k)
            
            mesh_to_render = grid_pv.extract_cells(mask_total) if has_selection else grid_pv

            if mesh_to_render.n_cells == 0:
                self.safe_remove("dynamic_mesh")
                for mid in range(5): self.safe_remove(f"mat_{mid}")
                self.update_text_info()
                pl.render()
                return

            if self.bmap_mode:
                # Mode B-Map: Xóa vật liệu
                for mid in range(5): self.safe_remove(f"mat_{mid}")
                
                if has_selection:
                    mesh_bmap = mesh_to_render 
                else:
                    mesh_bmap = mesh_to_render.threshold(0.1, scalars="MatID", preference="cell")

                if mesh_bmap.n_cells > 0:
                    self.safe_add_mesh(mesh_bmap, scalars="FluxB", cmap="jet", clim=[0, 1.5],
                                       show_edges=False, lighting=False,
                                       scalar_bar_args=sargs, show_scalar_bar=True,
                                       name="dynamic_mesh")
                else:
                    self.safe_remove("dynamic_mesh")
            else:
                # Mode Vật liệu: Xóa B-Map
                self.safe_remove("dynamic_mesh")
                if len(pl.scalar_bars) > 0: pl.scalar_bars.clear()

                for mid, color in colors.items():
                    try:
                        sub = mesh_to_render.threshold([mid, mid], scalars="MatID", preference="cell")
                    except ValueError: sub = pv.UnstructuredGrid()

                    if sub.n_cells > 0:
                        if has_selection: op = 1.0 
                        else: op = 0.05 if mid == 0 else 1.0 
                        
                        self.safe_add_mesh(sub, color=color, opacity=op, lighting=True,
                                           show_edges=True, edge_color="#333333", line_width=1,
                                           name=f"mat_{mid}")
                    else:
                        self.safe_remove(f"mat_{mid}")

            self.update_text_info()
            pl.render()

        def update_text_info(self):
            status_i = f"ON [{self.pos_i}/{N_I-1}]" if self.show_i else "OFF"
            status_j = f"ON [{self.pos_j}/{N_J-1}]" if self.show_j else "OFF"
            status_k = f"ON [{self.pos_k}/{N_K-1}]" if self.show_k else "OFF"
            
            info_text = (f"Frame: {self.current_frame}\n"
                         f"Layer R (i): {status_i}\n"
                         f"Layer Th(j): {status_j}\n"
                         f"Layer Z (k): {status_k}")
            pl.add_text(info_text, position="upper_left", font_size=9, name="info_text")

        # --- CONTROLS ---
        def toggle_play(self):
            self.is_playing = not self.is_playing
            if self.is_playing: self.timer.start(100)
            else: self.timer.stop()

        def next_frame(self):
            self.current_frame = (self.current_frame + 1) % self.total_frames
            self.render()
        
        def pre_frame(self):
            self.current_frame = (self.current_frame - 1) % self.total_frames
            self.render()

        def toggle_bmap(self, state):
            self.bmap_mode = state
            self.render()

        def toggle_show_i(self, state): self.show_i = state; self.render()
        def toggle_show_j(self, state): self.show_j = state; self.render()
        def toggle_show_k(self, state): self.show_k = state; self.render()

        def move_i(self, delta): self.pos_i = np.clip(self.pos_i + delta, 0, N_I-1); self.render()
        def move_j(self, delta): self.pos_j = (self.pos_j + delta) % N_J; self.render()
        def move_k(self, delta): self.pos_k = np.clip(self.pos_k + delta, 0, N_K-1); self.render()

    state = ViewerState()
    state.render()
    
    pl.reset_camera() # Chỉ reset camera lần đầu tiên khi mở app

    # --- 4. TẠO TOOLBAR ---
    tb = pl.app_window.addToolBar("Controls")

    # GROUP 1: DISPLAY MODE
    act_bmap = QAction("B-Map", pl.app_window)
    act_bmap.setCheckable(True)
    act_bmap.triggered.connect(state.toggle_bmap)
    tb.addAction(act_bmap)
    tb.addSeparator()

    # GROUP 2: LAYER CONTROLS (I, J, K)
    def add_ctrl_group(label, toggle_func, move_func, default_check=False):
        act_show = QAction(label, pl.app_window)
        act_show.setCheckable(True)
        act_show.setChecked(default_check)
        act_show.triggered.connect(toggle_func)
        tb.addAction(act_show)
        
        act_dec = QAction("-", pl.app_window)
        act_dec.triggered.connect(lambda: move_func(-1))
        tb.addAction(act_dec)
        
        act_inc = QAction("+", pl.app_window)
        act_inc.triggered.connect(lambda: move_func(1))
        tb.addAction(act_inc)
        
        dummy = QWidget(); dummy.setFixedWidth(15); tb.addWidget(dummy)

    add_ctrl_group("Layer R (i)", state.toggle_show_i, state.move_i, False)
    add_ctrl_group("Layer θ (j)", state.toggle_show_j, state.move_j, False)
    add_ctrl_group("Layer Z (k)", state.toggle_show_k, state.move_k, True)

    tb.addSeparator()

    # GROUP 3: PLAYBACK
    act_pre = QAction(pl.app_window.style().standardIcon(QStyle.SP_MediaSkipBackward), "", pl.app_window)
    act_pre.triggered.connect(state.pre_frame)
    tb.addAction(act_pre)

    act_play = QAction(pl.app_window.style().standardIcon(QStyle.SP_MediaPlay), "", pl.app_window)
    act_play.triggered.connect(state.toggle_play)
    tb.addAction(act_play)

    act_next = QAction(pl.app_window.style().standardIcon(QStyle.SP_MediaSkipForward), "", pl.app_window)
    act_next.triggered.connect(state.next_frame)
    tb.addAction(act_next)

    pl.show()
    pl.app.exec_()