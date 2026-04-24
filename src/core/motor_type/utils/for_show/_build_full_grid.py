from src.core.motor_type.utils.for_show._process_grid_indices import _process_grid_indices

def _build_full_grid(grid_sector, dim_sector, sym_factor):
    if sym_factor <= 1:
        return grid_sector, dim_sector
    
    step = 360.0 / sym_factor
    segments = [grid_sector.rotate_z(i * step) for i in range(sym_factor)]
    grid_full = segments[0].merge(segments[1:]).clean(tolerance=1e-5)
    dim_full = _process_grid_indices(grid_full)
    
    return grid_full, dim_full