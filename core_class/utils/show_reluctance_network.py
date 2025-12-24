import numpy as np
import pyvista as pv
from pyvistaqt import BackgroundPlotter
from PyQt5.QtWidgets import QDockWidget, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

def show_reluctance_network(reluctance_network, use_symmetry_factor=True):
    mesh_obj = reluctance_network.mesh
    elements_matrix = reluctance_network.elements
    nr, nt, nz = elements_matrix.shape
    
    grid_pv = mesh_obj.to_pyvista_grid()
    n_cells_sector = grid_pv.n_cells
    flat_elements = elements_matrix.flatten(order='F')
    
    mat_ids = np.zeros(n_cells_sector, dtype=int)
    b_values = np.zeros(n_cells_sector, dtype=float)

    for idx, el in enumerate(flat_elements):
        if el is None: 
            continue
        mat_name = str(el.material).lower()
        if "iron" in mat_name or "steel" in mat_name:
            mat_ids[idx] = 1
        elif "magnet" in mat_name:
            vec = getattr(el, 'magnetization_direction', None)
            z_val = vec[-1] if (vec is not None and len(vec) > 0) else 0
            mat_ids[idx] = 2 if z_val >= 0 else 4
        elif "coil" in mat_name or "winding" in mat_name:
            mat_ids[idx] = 3
        else:
            mat_ids[idx] = 0
        try:
            flux_avg = getattr(el, 'flux_density_average', None)
            b_values[idx] = flux_avg[-1] if (flux_avg is not None and len(flux_avg) > 0) else 0.0
        except:
            b_values[idx] = 0.0

    if use_symmetry_factor and hasattr(reluctance_network, 'symmetry_factor'):
        sym_factor = int(reluctance_network.symmetry_factor)
        if sym_factor > 1:
            angle_step = 360.0 / sym_factor
            segments = []
            for i in range(sym_factor):
                segments.append(grid_pv.rotate_z(i * angle_step))
            
            merged_grid = segments[0].merge(segments[1:])
            grid_pv = merged_grid.clean(tolerance=1e-5, remove_unused_points=True)
            
            mat_ids = np.tile(mat_ids, sym_factor)
            b_values = np.tile(b_values, sym_factor)
            grid_pv.cell_data["OrigID"] = np.tile(np.arange(n_cells_sector), sym_factor)
        else:
            grid_pv.cell_data["OrigID"] = np.arange(n_cells_sector)
    else:
        grid_pv.cell_data["OrigID"] = np.arange(n_cells_sector)

    grid_pv.cell_data["MatID"] = mat_ids
    grid_pv.cell_data["FluxB"] = b_values

    pl = BackgroundPlotter(title="Reluctance Network Viewer", window_size=(1600, 900))
    pl.set_background("#050505")
    pl.add_axes()

    dock = QDockWidget("Element Info", pl.app_window)
    dock_widget = QWidget()
    layout = QVBoxLayout()
    text_info = QTextEdit()
    text_info.setReadOnly(True)
    text_info.setStyleSheet("background-color: #1E1E1E; color: white; font-family: Consolas; font-size: 14px;")
    layout.addWidget(text_info)
    dock_widget.setLayout(layout)
    dock.setWidget(dock_widget)
    pl.app_window.addDockWidget(Qt.RightDockWidgetArea, dock)

    styles = {
        0: ("Air", "#AAAAAA"),
        1: ("Iron", "#F0F0F0"),
        2: ("Magnet N", "#FF0000"),
        3: ("Coil", "#FFAA00"),
        4: ("Magnet S", "#0000FF")
    }

    current_actors = []
    
    def render_view(is_bmap_mode, is_trans_checked):
        for actor in current_actors:
            pl.remove_actor(actor)
        current_actors.clear()
        solid_opacity = 1.0 if is_trans_checked else 0.5
        air_opacity = 0.3

        if is_bmap_mode:
            active_mesh = grid_pv.threshold(0.1, scalars="MatID", preference="cell")
            if active_mesh.n_cells > 0:
                actor_active = pl.add_mesh(active_mesh, scalars="FluxB", cmap="jet", clim=[0, 1.5],
                                         opacity=solid_opacity, show_edges=False, smooth_shading=True,
                                         scalar_bar_args={'title': "Flux Density (T)", 'color': 'white'})
                current_actors.append(actor_active)
            air_mesh = grid_pv.threshold([0, 0], scalars="MatID", preference="cell")
            if air_mesh.n_cells > 0:
                actor_air = pl.add_mesh(air_mesh, scalars="FluxB", cmap="jet", clim=[0, 2.0],
                                      opacity=air_opacity, show_edges=False, show_scalar_bar=False)
                current_actors.append(actor_air)
        else:
            for mat_id, (label, color) in styles.items():
                sub_mesh = grid_pv.threshold([mat_id, mat_id], scalars="MatID", preference="cell")
                if sub_mesh.n_cells > 0:
                    current_opacity = air_opacity if mat_id == 0 else solid_opacity
                    show_edges = True if (mat_id != 0 and is_trans_checked) else False
                    actor = pl.add_mesh(sub_mesh, color=color, opacity=current_opacity, 
                                      show_edges=show_edges, edge_color="#333333", 
                                      smooth_shading=True, label=label, pickable=True)
                    current_actors.append(actor)
            pl.add_legend(bcolor='#1A1A1A', border=True, size=(0.12, 0.15), loc='lower right')

    class ViewerState:
        def __init__(self):
            self.selected_idx = (0, 0, 0)
            self.highlight_actor = None 
            self.bmap_mode = False
            self.trans_checked = False
        def toggle_mode(self, state):
            self.bmap_mode = state
            render_view(self.bmap_mode, self.trans_checked)
            self.update_selection(*self.selected_idx)
        def toggle_transparency(self, state):
            self.trans_checked = state
            render_view(self.bmap_mode, self.trans_checked)
            self.update_selection(*self.selected_idx)
        def update_selection(self, ir, it, iz):
            self.selected_idx = (ir, it, iz)
            flat_id = ir + it * nr + iz * (nr * nt)
            if self.highlight_actor:
                pl.remove_actor(self.highlight_actor)
            try:
                target_cells = np.where(grid_pv.cell_data["OrigID"] == flat_id)[0]
                cell_geo = grid_pv.extract_cells(target_cells)
                self.highlight_actor = pl.add_mesh(cell_geo, style='wireframe', color='#00FFFF', 
                                                   line_width=5, render=False, name="highlight", lighting=False)
            except: pass
            el = elements_matrix[ir, it, iz]
            info_str = f"=== SELECTED ELEMENT ===\nIndex: [{ir}, {it}, {iz}]\nFlat ID: {flat_id}\n"
            info_str += f"Material: {styles[mat_ids[flat_id % n_cells_sector]][0]}\n"
            info_str += f"Flux B: {b_values[flat_id % n_cells_sector]:.4f} T\n" + "="*30 + "\n"
            if el is not None:
                for key, val in vars(el).items():
                    if key.startswith("__"): continue
                    info_str += f"\n[ {key} ]\n{val}\n"
            text_info.setText(info_str)
        def move_cursor(self, dr, dt, dz):
            r, t, z = self.selected_idx
            r, t, z = (r + dr) % nr, (t + dt) % nt, (z + dz) % nz
            self.update_selection(r, t, z)

    state = ViewerState()
    render_view(False, False)
    def on_cell_picked(picked_mesh):
        if picked_mesh is None or "OrigID" not in picked_mesh.cell_data: return
        oid = picked_mesh.cell_data["OrigID"][0]
        state.update_selection(oid % nr, (oid % (nr * nt)) // nr, oid // (nr * nt))

    pl.enable_cell_picking(callback=on_cell_picked, show=False)
    btn_size, gap, x1, x2, y = 80, 10, 20, 20 + 80 + 10, pl.window_size[1] - 120
    btns = [("k++", (x2, y), (0,0,1)), ("k--", (x1, y), (0,0,-1)), ("j++", (x2, y-90), (0,1,0)), 
            ("j--", (x1, y-90), (0,-1,0)), ("i++", (x2, y-180), (1,0,0)), ("i--", (x1, y-180), (-1,0,0))]
    for lbl, pos, move in btns:
        pl.add_checkbox_button_widget(lambda v, m=move: state.move_cursor(*m), position=pos, size=btn_size, color_on='grey', color_off='grey')
        pl.add_text(lbl, position=(pos[0] + 25, pos[1] + 25), font_size=14)
    pl.add_checkbox_button_widget(state.toggle_mode, position=(x2, y-270), size=btn_size, color_on='red', color_off='grey')
    pl.add_text("B-Map", position=(x2 + 15, y-245), font_size=14)
    pl.add_checkbox_button_widget(state.toggle_transparency, position=(x1, y-270), size=btn_size, color_on='cyan', color_off='grey')
    pl.add_text("Transp.", position=(x1 + 10, y-245), font_size=14)
    state.update_selection(0, 0, 0)
    pl.show()
    pl.app.exec_()