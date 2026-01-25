import numpy as np
import pyvista as pv
from pyvistaqt import BackgroundPlotter, QtInteractor

def display_reluctance_network(reluctance_network, plotter=None):
    if reluctance_network is None or reluctance_network.elements is None: 
        return
        
    # Tạo lưới từ CylindricalMesh
    grid = reluctance_network.mesh.to_pyvista_grid()
    elements_flat = reluctance_network.elements.flatten(order='F')
    
    # Kiểm tra khớp dữ liệu giữa lưới và số lượng phần tử
    if grid.n_cells != len(elements_flat):
        print(f"[Display] Mismatch: Grid cells ({grid.n_cells}) != Elements ({len(elements_flat)})")
        return

    mat_ids = np.zeros(len(elements_flat), dtype=int)
    for idx, el in enumerate(elements_flat):
        if el is None: continue
        m = el.material.lower()
        if "iron" in m: mat_ids[idx] = 1
        elif "magnet" in m:
            z_val = el.magnetization_direction[-1] if el.magnetization_direction is not None else 0
            mat_ids[idx] = 2 if z_val >= 0 else 4
        elif "coil" in m: mat_ids[idx] = 3
            
    grid.cell_data["MatID"] = mat_ids
    
    pl = plotter if plotter else BackgroundPlotter()
    pl.clear() 
    
    colors_net = {0: "#444444", 1: "#1976D2", 2: "#FF3333", 3: "#FF9900", 4: "#3366FF"}
    
    has_mesh = False
    for mid, col in colors_net.items():
        try:
            # Lọc phần tử theo vật liệu
            sub = grid.threshold([mid, mid], scalars="MatID")
            if sub.n_cells > 0:
                has_mesh = True
                op = 0.05 if mid == 0 else 1.0
                pl.add_mesh(sub, color=col, opacity=op, lighting=True, 
                            show_edges=True, edge_color="#333333", name=f"mat_{mid}")
        except: pass
    
    if not has_mesh:
        print("[Display] Warning: No cells passed the threshold.")
        
    pl.reset_camera()
    
    if plotter:
        pl.update()
        pl.render() # Ép buộc render ra khung hình nhúng
    else:
        pl.show()