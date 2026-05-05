import numpy as np

def _update_limits(viewer_state):
    dims = viewer_state.dim_full if (viewer_state.use_symmetry and viewer_state.grid_full) else viewer_state.dim_sector
    viewer_state.max_i, viewer_state.max_j, viewer_state.max_k = dims
    viewer_state.pos_i = np.clip(viewer_state.pos_i, 0, viewer_state.max_i - 1)
    viewer_state.pos_j = np.clip(viewer_state.pos_j, 0, viewer_state.max_j - 1)
    viewer_state.pos_k = np.clip(viewer_state.pos_k, 0, viewer_state.max_k - 1)