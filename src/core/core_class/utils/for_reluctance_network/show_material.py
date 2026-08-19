import numpy as np
import pyvista as pv

def show_material(reluctance_network, plotter=None):
    if plotter is None:
        return None

    pv.global_theme.line_width = 1.0

    grid = reluctance_network.mesh.to_pyvista_grid()
    elements_3d = reluctance_network.elements
    ni, nj, nk = elements_3d.shape

    mat_ids = np.zeros(grid.n_cells, dtype=int)
    for i in range(ni):
        for j in range(nj):
            for k in range(nk):
                el = elements_3d[i, j, k]
                if el:
                    m = str(el.material).lower()
                    idx = i + j * ni + k * ni * nj
                    if "iron" in m or "steel" in m:
                        mat_ids[idx] = 1
                    elif "magnet" in m:
                        mat_ids[idx] = 2
                    elif "coil" in m or "winding" in m or "copper" in m:
                        mat_ids[idx] = 3
                    else:
                        mat_ids[idx] = 0

    grid.cell_data["MatID"] = mat_ids

    # Bảng màu đơn sắc: Đen, Trắng, Xám
    # 0: Không khí (Air)        -> Xám đen nhạt (#2B2B2B)
    # 1: Lõi thép (Iron Core)   -> Xám kim loại (#B0B0B0)
    # 2: Nam châm (Magnet)      -> Xám trắng sáng (#E0E0E0)
    # 3: Cuộn dây (Coil/Winding)-> Xám đậm (#555555)
    colors_net = {
        0: "#2B2B2B",
        1: "#B0B0B0",
        2: "#E0E0E0",
        3: "#555555"
    }

    if hasattr(plotter, 'scalar_bars') and plotter.scalar_bars:
        plotter.scalar_bars.clear()

    for mid, col in colors_net.items():
        try:
            sub = grid.threshold([mid, mid], scalars="MatID")
            op = 0.05 if mid == 0 else 1.0
            plotter.add_mesh(
                sub,
                color=col,
                opacity=op,
                lighting=True,
                ambient=0.4,
                diffuse=0.7,
                specular=0.1,
                show_edges=True,
                edge_color="#1A1A1A",
                line_width=1.0,
                name=f"mat_{mid}",
                pickable=False
            )
        except Exception:
            if hasattr(plotter, 'remove_actor'):
                plotter.remove_actor(f"mat_{mid}")

    if hasattr(plotter, 'enable_trackball_style'):
        plotter.enable_trackball_style()

    return grid