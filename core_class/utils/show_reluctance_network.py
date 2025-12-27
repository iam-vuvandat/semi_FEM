import numpy as np
import pyvista as pv
from pyvistaqt import BackgroundPlotter
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
    # Lấy danh sách lịch sử ElementLite
    history = reluctance_network.list_elements_lite
    if not history:
        print("[Error] No ElementLite history found.")
        return

    mesh_obj = reluctance_network.mesh
    grid_pv = mesh_obj.to_pyvista_grid()
    n_cells_sector = grid_pv.n_cells
    
    # Cấu hình Plotter
    pl = BackgroundPlotter(title="Reluctance Network Animation", window_size=(1600, 900))
    pl.set_background("#050505")
    pl.add_axes()

    # Định nghĩa màu sắc vật liệu
    colors = {0: "#444444", 1: "#E0E0E0", 2: "#FF3333", 3: "#FF9900", 4: "#3366FF"}

    sargs = dict(
        title="Flux Density (T)", title_font_size=20, label_font_size=16,
        n_labels=6, fmt="%.2f", vertical=True, position_x=0.92, position_y=0.15,
        height=0.7, width=0.04, color='white', shadow=False
    )

    class ViewerState:
        def __init__(self):
            self.current_frame = 0
            self.total_frames = len(history)
            self.bmap_mode = False
            self.solid_mode = False
            self.is_playing = False
            self.current_actors = []
            
            # Timer cho chế độ Play
            self.timer = QTimer()
            self.timer.timeout.connect(self.next_frame)

        def get_current_data(self):
            # Lấy mảng ElementLite 3D tại frame hiện tại và làm phẳng
            elements_lite = history[self.current_frame].flatten(order='F')
            
            mat_ids = np.zeros(n_cells_sector, dtype=int)
            b_values = np.zeros(n_cells_sector, dtype=float)

            for idx, el in enumerate(elements_lite):
                if el is None: continue
                # Phân loại vật liệu
                m_name = el.material.lower()
                if "iron" in m_name or "steel" in m_name: mat_ids[idx] = 1
                elif "magnet" in m_name:
                    z_val = el.magnetization_direction[-1] if el.magnetization_direction is not None else 0
                    mat_ids[idx] = 2 if z_val >= 0 else 4
                elif "coil" in m_name or "winding" in m_name: mat_ids[idx] = 3
                
                # Lấy FluxB
                if el.flux_density_average is not None:
                    b_values[idx] = el.flux_density_average[-1]

            # Xử lý đối xứng nếu có
            if use_symmetry_factor and hasattr(reluctance_network, 'symmetry_factor'):
                sym = int(reluctance_network.symmetry_factor)
                if sym > 1:
                    mat_ids = np.tile(mat_ids, sym)
                    b_values = np.tile(b_values, sym)
            
            return mat_ids, b_values

        def render(self):
            for actor in self.current_actors:
                pl.remove_actor(actor)
            self.current_actors.clear()
            
            if hasattr(pl, 'scalar_bars'):
                pl.scalar_bars.clear()

            mat_ids, b_values = self.get_current_data()
            grid_pv.cell_data["MatID"] = mat_ids
            grid_pv.cell_data["FluxB"] = b_values
            
            # Xử lý Symmetry Hình học (chỉ merge một lần đầu hoặc nếu grid thay đổi)
            non_air_mask = grid_pv.threshold(0.1, scalars="MatID", preference="cell")
            
            opacity_val = 1.0 if self.solid_mode else 0.4
            
            if self.bmap_mode:
                if non_air_mask.n_cells > 0:
                    actor = pl.add_mesh(non_air_mask, scalars="FluxB", cmap="jet", clim=[0, 1.8],
                                       opacity=opacity_val, show_edges=False, lighting=False,
                                       scalar_bar_args=sargs, show_scalar_bar=True)
                    self.current_actors.append(actor)
            else:
                for mid, color in colors.items():
                    sub = grid_pv.threshold([mid, mid], scalars="MatID", preference="cell")
                    if sub.n_cells > 0:
                        op = 0.05 if mid == 0 else opacity_val
                        actor = pl.add_mesh(sub, color=color, opacity=op, lighting=False,
                                          show_edges=self.solid_mode, edge_color="#222222")
                        self.current_actors.append(actor)
            
            # Hiển thị số Frame hiện tại lên màn hình
            pl.add_text(f"Frame: {self.current_frame}/{self.total_frames-1}", 
                        position="upper_left", font_size=10, color='white', name="frame_info")

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

        def toggle_play(self, state):
            self.is_playing = state
            if self.is_playing:
                self.timer.start(100) # Chạy mỗi 100ms
            else:
                self.timer.stop()

    state = ViewerState()
    
    # Thiết lập Symmetry Hình học một lần duy nhất để tối ưu
    if use_symmetry_factor and hasattr(reluctance_network, 'symmetry_factor'):
        sym_factor = int(reluctance_network.symmetry_factor)
        if sym_factor > 1:
            angle_step = 360.0 / sym_factor
            segments = [grid_pv.rotate_z(i * angle_step) for i in range(sym_factor)]
            grid_pv = segments[0].merge(segments[1:]).clean(tolerance=1e-5)

    state.render()

    # Hệ thống nút bấm
    btn_size, gap = 80, 10
    x_start, y = 20, pl.window_size[1] - 120
    
    # Nút chức năng hiển thị
    pl.add_checkbox_button_widget(state.toggle_solid, position=(x_start, y), size=btn_size, color_on='cyan', color_off='grey')
    pl.add_text("Solid", position=(x_start + 25, y + 35), font_size=8, color='white')
    
    pl.add_checkbox_button_widget(state.toggle_bmap, position=(x_start + btn_size + gap, y), size=btn_size, color_on='red', color_off='grey')
    pl.add_text("B", position=(x_start + btn_size + gap + 35, y + 35), font_size=8, color='white')

    # Nút điều khiển Animation (Next, Pre, Play)
    x_ctrl = x_start + (btn_size + gap) * 2 + 50
    
    pl.add_checkbox_button_widget(lambda v: state.pre_frame(), position=(x_ctrl, y), size=btn_size, color_on='grey', color_off='grey')
    pl.add_text("Pre", position=(x_ctrl + 30, y + 35), font_size=8, color='white')

    pl.add_checkbox_button_widget(state.toggle_play, position=(x_ctrl + btn_size + gap, y), size=btn_size, color_on='green', color_off='grey')
    pl.add_text("Play", position=(x_ctrl + btn_size + gap + 30, y + 35), font_size=8, color='white')

    pl.add_checkbox_button_widget(lambda v: state.next_frame(), position=(x_ctrl + (btn_size + gap)*2, y), size=btn_size, color_on='grey', color_off='grey')
    pl.add_text("Next", position=(x_ctrl + (btn_size + gap)*2 + 25, y + 35), font_size=8, color='white')

    pl.show()
    pl.app.exec_()