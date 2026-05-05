import numpy as np
import pyvista as pv

def render(viewer_state):
    if viewer_state.show_geometry:
        viewer_state._safe_remove("dynamic_mesh")
        for mid in range(5): viewer_state._safe_remove(f"mat_{mid}")
        viewer_state.update_text_info()
        viewer_state.pl.render()
        return
    grid = viewer_state.active_grid
    mat_ids, b_vals = viewer_state.get_current_data()
    grid.cell_data["MatID"], grid.cell_data["FluxB"] = mat_ids, b_vals
    mask = np.zeros(grid.n_cells, dtype=bool)
    has_sel = viewer_state.show_i or viewer_state.show_j or viewer_state.show_k
    if not has_sel: mask[:] = True
    else:
        if viewer_state.show_i: mask |= (grid.cell_data["idx_i"] == viewer_state.pos_i)
        if viewer_state.show_j: mask |= (grid.cell_data["idx_j"] == viewer_state.pos_j)
        if viewer_state.show_k: mask |= (grid.cell_data["idx_k"] == viewer_state.pos_k)
    try: render_mesh = grid.extract_cells(mask)
    except Exception: render_mesh = pv.UnstructuredGrid()
    if render_mesh.n_cells == 0:
        viewer_state._safe_remove("dynamic_mesh")
        for mid in range(5): viewer_state._safe_remove(f"mat_{mid}")
        viewer_state.update_text_info()
        viewer_state.pl.render()
        return
    if viewer_state.bmap_mode:
        for mid in range(5): viewer_state._safe_remove(f"mat_{mid}")
        target = render_mesh if has_sel else render_mesh.threshold(0.1, scalars="MatID")
        if target.n_cells > 0:
            viewer_state._safe_add(target, scalars="FluxB", cmap="jet", clim=[0, 2.0],
                            lighting=False, scalar_bar_args=viewer_state.sargs, show_scalar_bar=True, name="dynamic_mesh")
        else: viewer_state._safe_remove("dynamic_mesh")
    else:
        viewer_state._safe_remove("dynamic_mesh")
        if viewer_state.pl.scalar_bars: viewer_state.pl.scalar_bars.clear()
        for mid, col in viewer_state.colors_net.items():
            try:
                sub = render_mesh.threshold([mid, mid], scalars="MatID")
                op = 1.0 if has_sel else (0.05 if mid == 0 else 1.0)
                actual_col = "#B0B0B0" if mid == 1 else col
                viewer_state._safe_add(sub, color=actual_col, opacity=op, lighting=True, 
                               ambient=0.4, diffuse=0.7, specular=0.1,
                               show_edges=True, edge_color="#333333", name=f"mat_{mid}")
            except Exception: viewer_state._safe_remove(f"mat_{mid}")
    viewer_state.update_text_info()
    viewer_state.pl.render()