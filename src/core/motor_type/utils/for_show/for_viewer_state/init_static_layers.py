import numpy as np
import pyvista as pv

def init_static_layers(viewer_state):
    if viewer_state.geometry_obj and viewer_state.geometry_obj.geometry:
        for idx, seg in enumerate(viewer_state.geometry_obj.geometry):
            if seg.mesh is None: continue
            mat = str(seg.material).lower()
            color = "#3498DB" 
            if "iron" in mat or "steel" in mat: color = "#B0B0B0" 
            elif "magnet" in mat: color = "#E74C3C"
            elif "copper" in mat or "coil" in mat: color = "#E67E22"
            elif "air" in mat: color = "#E0F7FA"
            op = 0.15 if "air" in mat else 1.0
            pv_mesh = pv.wrap(seg.mesh) if not isinstance(seg.mesh, pv.DataSet) else seg.mesh
            viewer_state.pl.add_mesh(pv_mesh, color=color, opacity=op, lighting=True, 
                        specular=0.1, ambient=0.4, diffuse=0.7, name=f"geo_full_{idx}")
            sector_mesh = pv_mesh.copy()
            if viewer_state.sym_factor > 1:
                try:
                    theta_rad = np.radians(360.0 / viewer_state.sym_factor)
                    sector_mesh = sector_mesh.clip(normal=(0, -1, 0), origin=(0, 0, 0))
                    n_clip = (-np.sin(theta_rad), np.cos(theta_rad), 0)
                    sector_mesh = sector_mesh.clip(normal=n_clip, origin=(0, 0, 0))
                except Exception:
                    pass
            viewer_state.pl.add_mesh(sector_mesh, color=color, opacity=op, lighting=True, 
                        specular=0.1, ambient=0.4, diffuse=0.7, name=f"geo_sec_{idx}")
    viewer_state._redraw_wireframe()
    viewer_state.update_static_visibility()