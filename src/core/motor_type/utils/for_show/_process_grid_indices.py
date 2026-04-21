import numpy as np 

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