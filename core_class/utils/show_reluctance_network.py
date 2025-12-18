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

def show_reluctance_network(reluctance_network):
    mesh_obj = reluctance_network.mesh
    elements_matrix = reluctance_network.elements
    
    nr, nt, nz = elements_matrix.shape
    
    grid_pv = mesh_obj.to_pyvista_grid()
    
    flat_elements = elements_matrix.flatten(order='F')
    
    grid_pv.cell_data["OrigID"] = np.arange(grid_pv.n_cells)
    
    mat_ids = np.zeros(len(flat_elements), dtype=int)
    b_values = np.zeros(len(flat_elements), dtype=float)

    for idx, el in enumerate(flat_elements):
        if el is None: 
            continue
        
        mat_name = str(el.material).lower()
        if "iron" in mat_name or "steel" in mat_name:
            mat_ids[idx] = 1
        elif "magnet" in mat_name:
            vec = getattr(el, 'magnetization_direction', None)
            z_val = vec[-1] if (vec is not None and len(vec) > 0) else 0
            if z_val > 0:
                mat_ids[idx] = 2 
            elif z_val < 0:
                mat_ids[idx] = 4 
            else:
                mat_ids[idx] = 2
        elif "coil" in mat_name or "winding" in mat_name:
            mat_ids[idx] = 3
        else:
            mat_ids[idx] = 0

        try:
            flux_avg = getattr(el, 'flux_density_average', None)
            if flux_avg is not None and len(flux_avg) > 0:
                b_values[idx] = flux_avg[-1]
            else:
                b_values[idx] = 0.0
        except Exception:
            b_values[idx] = 0.0
            
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
        0: ("Default/Air", "#AAAAAA", 0.1),
        1: ("Iron",        "#F0F0F0", 1.0),
        2: ("Magnet N",    "#FF0000", 1.0),
        3: ("Coil",        "#FFAA00", 1.0),
        4: ("Magnet S",    "#0000FF", 1.0)
    }

    current_actors = []
    
    def render_view(is_bmap_mode, is_trans_checked):
        for actor in current_actors:
            pl.remove_actor(actor)
        current_actors.clear()

        # Xác định độ trong suốt dựa trên nút bấm (theo yêu cầu của bạn)
        # Bật (Checked) = 1.0 (Đặc), Tắt (Unchecked) = 0.5 (Trong suốt)
        solid_opacity = 1.0 if is_trans_checked else 0.5
        air_opacity = 0.3  # Giữ cố định 0.3 cho không khí như bạn yêu cầu

        if is_bmap_mode:
            # --- Chế độ B-Map ---
            # Phần vật liệu rắn (Iron, Magnet...)
            active_mesh = grid_pv.threshold(0.1, scalars="MatID", preference="cell")
            if active_mesh.n_cells > 0:
                actor_active = pl.add_mesh(
                    active_mesh, 
                    scalars="FluxB", 
                    cmap="jet", 
                    clim=[0, 1.5],
                    opacity=solid_opacity,  # <--- Đã sửa: dùng biến thay vì số cứng 0.5
                    show_edges=False,
                    scalar_bar_args={'title': "Flux Density (T)", 'color': 'white'}
                )
                current_actors.append(actor_active)

            # Phần không khí
            air_mesh = grid_pv.threshold([0, 0], scalars="MatID", preference="cell")
            if air_mesh.n_cells > 0:
                actor_air = pl.add_mesh(
                    air_mesh,
                    scalars="FluxB",
                    cmap="jet",
                    clim=[0, 2.0],
                    opacity=air_opacity, # <--- Đã sửa: dùng biến 0.3
                    show_edges=False,
                    show_scalar_bar=False
                )
                current_actors.append(actor_air)
                
        else:
            # --- Chế độ Material ---
            for mat_id, (label, color, _) in styles.items():
                sub_mesh = grid_pv.threshold([mat_id, mat_id], scalars="MatID", preference="cell")
                if sub_mesh.n_cells > 0:
                    edge_color = "#222222" if mat_id == 0 else "#555555"
                    style = 'surface'
                    
                    if mat_id == 0:
                        # Vật liệu là khí (Air)
                        current_opacity = air_opacity
                        show_edges = False
                    else:
                        # Vật liệu rắn (Iron, Magnet, Coil...)
                        current_opacity = solid_opacity
                        # Nếu đặc hoàn toàn (1.0) thì hiện cạnh, nếu trong suốt (0.5) thì ẩn cạnh cho đẹp
                        show_edges = True if is_trans_checked else False

                    actor = pl.add_mesh(
                        sub_mesh, 
                        color=color, 
                        opacity=current_opacity, 
                        show_edges=show_edges, 
                        edge_color=edge_color, 
                        label=label,
                        pickable=True, 
                        style=style
                    )
                    current_actors.append(actor)
            
            if not is_bmap_mode:
                pl.add_legend(bcolor='#1A1A1A', border=True, size=(0.12, 0.15), loc='lower right', face='rectangle')
    
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
                cell_geo = grid_pv.extract_cells([flat_id])
                self.highlight_actor = pl.add_mesh(cell_geo, style='wireframe', color='#00FFFF', 
                                                   line_width=5, render=False, name="highlight", lighting=False)
            except: pass

            element_obj = elements_matrix[ir, it, iz]
            
            info_str = f"=== SELECTED ELEMENT ===\n"
            info_str += f"Index (3D): [{ir}, {it}, {iz}]\n"
            info_str += f"Flat ID   : {flat_id}\n"
            info_str += f"Material  : {styles[mat_ids[flat_id]][0]}\n"
            
            b_val = b_values[flat_id]
            info_str += f"Flux B    : {b_val:.4f} T\n"
            info_str += "="*30 + "\n"
            
            if element_obj is None:
                info_str += "Status: Empty / None"
            else:
                attrs = vars(element_obj)
                for key, val in attrs.items():
                    if key.startswith("__"): continue
                    
                    info_str += f"\n[ {key} ]\n"
                    
                    if isinstance(val, np.ndarray):
                        with np.printoptions(formatter={'float': '{: 0.6f}'.format}, threshold=1000, linewidth=40):
                            arr_str = np.array2string(val, separator=', ')
                            info_str += f"{arr_str}\n"
                    elif isinstance(val, float):
                        info_str += f"{val:.9f}\n"
                    elif key in ['mesh', 'motor', 'geometry']:
                        info_str += f"<Reference to {type(val).__name__}>\n"
                    else:
                        info_str += f"{val}\n"

            text_info.setText(info_str)

        def move_cursor(self, dr, dt, dz):
            r, t, z = self.selected_idx
            r += dr
            t += dt
            z += dz

            while r >= nr: r -= nr; t += 1
            while r < 0:   r += nr; t -= 1
            while t >= nt: t -= nt; z += 1
            while t < 0:   t += nt; z -= 1
            z = z % nz 

            self.update_selection(r, t, z)

    state = ViewerState()
    render_view(False, False)

    def on_cell_picked(picked_mesh):
        if picked_mesh is None: return
        if isinstance(picked_mesh, pv.MultiBlock):
            if len(picked_mesh) == 0: return
            picked_mesh = picked_mesh[0]

        if not hasattr(picked_mesh, 'n_cells') or picked_mesh.n_cells == 0:
            return

        if "OrigID" in picked_mesh.cell_data:
            original_id = picked_mesh.cell_data["OrigID"][0]
            iz = original_id // (nr * nt)
            rem = original_id % (nr * nt)
            it = rem // nr
            ir = rem % nr
            state.update_selection(ir, it, iz)

    pl.enable_cell_picking(mesh=None, callback=on_cell_picked, show=False, 
                           show_message=False, through=False, use_hardware=False)

    btn_size = 80
    gap = 10
    x_col1 = 20
    x_col2 = x_col1 + btn_size + gap
    y_row1 = pl.window_size[1] - 120
    
    buttons = [
        ("k++", (x_col2, y_row1), lambda: state.move_cursor(0, 0, 1)),
        ("k--", (x_col1, y_row1), lambda: state.move_cursor(0, 0, -1)),
        ("j++", (x_col2, y_row1 - (btn_size+gap)), lambda: state.move_cursor(0, 1, 0)),
        ("j--", (x_col1, y_row1 - (btn_size+gap)), lambda: state.move_cursor(0, -1, 0)),
        ("i++", (x_col2, y_row1 - 2*(btn_size+gap)), lambda: state.move_cursor(1, 0, 0)),
        ("i--", (x_col1, y_row1 - 2*(btn_size+gap)), lambda: state.move_cursor(-1, 0, 0)),
    ]

    for label, pos, func in buttons:
        pl.add_checkbox_button_widget(lambda v, f=func: f(), position=pos, size=btn_size, color_on='grey', color_off='grey')
        pl.add_text(label, position=(pos[0] + 25, pos[1] + 25), font_size=14, color='white')

    y_last_row = y_row1 - 3*(btn_size+gap)

    bmap_pos = (x_col2, y_last_row)
    pl.add_checkbox_button_widget(state.toggle_mode, position=bmap_pos, size=btn_size, color_on='red', color_off='grey')
    pl.add_text("B-Map", position=(bmap_pos[0] + 15, bmap_pos[1] + 25), font_size=14, color='white')

    trans_pos = (x_col1, y_last_row)
    pl.add_checkbox_button_widget(state.toggle_transparency, position=trans_pos, size=btn_size, color_on='cyan', color_off='grey')
    pl.add_text("Transp.", position=(trans_pos[0] + 10, trans_pos[1] + 25), font_size=14, color='black')

    state.update_selection(0, 0, 0)
    pl.show()
    pl.app.exec_()