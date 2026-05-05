import numpy as np

def get_current_data(viewer_state):
    n_cells = viewer_state.active_grid.n_cells
    if not viewer_state.has_results or viewer_state.total_frames == 0:
        return np.zeros(n_cells, dtype=int), np.zeros(n_cells)
    el_lite = viewer_state.history[viewer_state.current_frame].flatten(order='F')
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
    if viewer_state.use_symmetry and viewer_state.sym_factor > 1:
        return np.tile(mat_sec, viewer_state.sym_factor), np.tile(b_sec, viewer_state.sym_factor)
    return mat_sec, b_sec