import numpy as np
import pyvista as pv
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

class Geometry:
    def __init__(self, geometry=None):
        self.geometry = geometry if geometry is not None else []

    def show(self, 
             plotter=None,             
             iron_color="#A0A0A0",    
             magnet_color="#FF3333",  
             coil_color="#FF8C00",    
             air_color="#CCEEFF",     
             default_color="#3498DB",
             highlight_color="#00FF00"):
        
        if not self.geometry:
            print("Geometry is empty.")
            return

        if plotter is None:
            pv.set_plot_theme("dark")
            pl = pv.Plotter(window_size=[1200, 900])
            pl.set_background("#0F0F0F") 
            pl.add_axes()
            try:
                pl.enable_anti_aliasing('msaa')
            except: pass
            own_plotter = True
        else:
            pl = plotter
            own_plotter = False

        selection_state = {'last_mesh': None}

        for segment in self.geometry:
            mesh_data = segment.mesh
            if mesh_data is None: continue

            try:
                pv_mesh = pv.wrap(mesh_data)
                pv_mesh = pv_mesh.clean()
                pv_mesh = pv_mesh.compute_normals(point_normals=True, 
                                                  split_vertices=True, 
                                                  feature_angle=30.0, 
                                                  inplace=True)
            except:
                continue

            mat = str(segment.material).lower()
            color = default_color
            opacity = 1.0; pbr = True; metallic = 0.5; roughness = 0.5

            if "iron" in mat or "steel" in mat: 
                color = iron_color; metallic = 0.8; roughness = 0.3 
            elif "magnet" in mat: 
                color = magnet_color; metallic = 0.2; roughness = 0.6
            elif "copper" in mat or "coil" in mat: 
                color = coil_color; metallic = 0.9; roughness = 0.2 
            elif "air" in mat: 
                color = air_color; opacity = 0.05; pbr = False

            lines = [f"{'ATTRIBUTE':<22} : {'VALUE'}", "-" * 45]
            attrs = [a for a in dir(segment) if not a.startswith('__') and not callable(getattr(segment, a))]
            priority_keys = ['material', 'index', 'r_length', 't_length', 'z_length']
            attrs.sort(key=lambda x: (0 if x in priority_keys else 1, x))

            for attr in attrs:
                if attr == 'mesh': continue
                value = getattr(segment, attr)
                val_str = str(value)
                if value is None: val_str = "None"
                elif isinstance(value, float): val_str = f"{value:.4f}"
                elif isinstance(value, (np.ndarray, list)):
                    try:
                        v = np.array(value).flatten()
                        if len(v) <= 3: val_str = "[" + ", ".join([f"{x:.2f}" for x in v]) + "]"
                        else: val_str = f"Array {np.shape(value)}"
                    except: pass
                lines.append(f"{attr:<22} : {val_str}")

            full_info = "\n".join(lines)
            pv_mesh.field_data["info"] = [full_info]

            actor = pl.add_mesh(pv_mesh, 
                                color=color, 
                                opacity=opacity,
                                show_edges=False,       
                                smooth_shading=True,   
                                pbr=pbr,               
                                metallic=metallic,
                                roughness=roughness,
                                pickable=True)
            
            pv_mesh._actor_ref = actor
            pv_mesh._original_color = actor.prop.color 

        def on_pick(mesh):
            if mesh is None: return
            
            actor = getattr(mesh, '_actor_ref', None)
            if actor is None: return

            original_color = getattr(mesh, '_original_color', None)
            last_mesh = selection_state['last_mesh']

            if last_mesh is mesh:
                if original_color:
                    actor.prop.color = original_color
                
                selection_state['last_mesh'] = None
                pl.add_text("Select a segment...", position='upper_left', font_size=10, color='gray', name='hud_info')
                return

            if last_mesh is not None:
                old_actor = getattr(last_mesh, '_actor_ref', None)
                old_orig_color = getattr(last_mesh, '_original_color', None)
                if old_actor and old_orig_color:
                    old_actor.prop.color = old_orig_color
            
            actor.prop.color = highlight_color
            selection_state['last_mesh'] = mesh
            
            try:
                if "info" in mesh.field_data:
                    pl.add_text(
                        f"== SELECTED SEGMENT ==\n{mesh.field_data['info'][0]}", 
                        position='upper_left', 
                        font_size=10, 
                        color='white', 
                        name='hud_info', 
                        font='courier', 
                        shadow=True
                    )
            except: pass

        pl.enable_mesh_picking(on_pick, show=False, show_message=False)

        if own_plotter:
            if not pl.renderer.lights:
                pl.add_text("INTERACTIVE 3D VIEW", position='upper_right', font_size=12, color='gray')
                light = pv.Light(position=(1000, 1000, 1000), color='white', intensity=0.8)
                pl.add_light(light)
            
            pl.view_isometric()
            pl.show()
            
        return pl