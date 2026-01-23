import numpy as np
import pyvista as pv
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

class Geometry:
    def __init__(self, geometry=None):
        self.geometry = geometry if geometry is not None else []

    def _add_cylindrical_axes(self, pl, length=100):
        origin = np.array([0, 0, 0])
        arrow_params = {'tip_length': 0.1, 'tip_radius': 0.03, 'shaft_radius': 0.01, 'scale': length}

        pl.add_mesh(pv.Arrow(start=origin, direction=[0, 0, 1], **arrow_params), color='#2980B9', lighting=False, name='z_axis_arrow')
        pl.add_mesh(pv.Arrow(start=origin, direction=[1, 0, 0], **arrow_params), color='#C0392B', lighting=False, name='r_axis_arrow')
        
        radius_theta = length * 0.9 
        angle_rad = np.deg2rad(35)
        p_start, p_end = [radius_theta, 0, 0], [radius_theta * np.cos(angle_rad), radius_theta * np.sin(angle_rad), 0]
        
        # SỬA LỖI: Sử dụng keyword arguments cho CircularArc
        theta_arc = pv.CircularArc(pointa=p_start, pointb=p_end, center=origin)
        pl.add_mesh(theta_arc, color='#27AE60', line_width=4, name='theta_arc_line')

        pl.add_mesh(pv.Cone(center=p_end, direction=[-np.sin(angle_rad), np.cos(angle_rad), 0], 
                            height=length * 0.08, radius=length * 0.025, resolution=20), 
                    color='#27AE60', lighting=False, name='theta_axis_tip')

        offset = length * 0.1
        label_points = [origin - [offset*0.3, offset*0.3, 0], [0, 0, length + offset], [length + offset, 0, 0], 
                        [radius_theta * 1.1 * np.cos(angle_rad/2), radius_theta * 1.1 * np.sin(angle_rad/2), 0]]
        pl.add_point_labels(label_points, ["O", "z", "r", "θ"], font_size=25, text_color='black', shape=None, show_points=False, always_visible=True, name='axis_labels')

    def show(self, plotter=None, iron_color="#D3D3D3", magnet_color="#E74C3C", coil_color="#E67E22", 
             air_color="#E0F7FA", default_color="#3498DB", highlight_color="#FF00FF", show_axes=True):
        
        if not self.geometry:
            print("Geometry is empty.")
            return

        pv.set_plot_theme("document")
        if plotter is None:
            pl = pv.Plotter(window_size=[1600, 1200])
            pl.set_background("white") 
            try: pl.enable_anti_aliasing('msaa')
            except: pass
            own_plotter = True
        else:
            pl = plotter
            own_plotter = False

        # --- HIỆU ỨNG ÁNH SÁNG & CHIỀU SÂU (MỚI) ---
        pl.enable_shadows()             # Tạo bóng đổ giữa các linh kiện chồng lên nhau
        pl.enable_eye_dome_lighting()    # Làm nổi bật các cạnh và hốc sâu (rãnh stator)
        
        if show_axes:
            max_val = 100
            try:
                all_bounds = []
                for s in self.geometry:
                    if s.mesh is not None: all_bounds.extend(pv.wrap(s.mesh).bounds)
                if all_bounds: max_val = max([abs(x) for x in all_bounds])
            except: pass
            self._add_cylindrical_axes(pl, length=max_val * 1.3)

        selection_state = {'last_mesh': None}

        for segment in self.geometry:
            mesh_data = segment.mesh
            if mesh_data is None: continue

            try:
                pv_mesh = pv.wrap(mesh_data).clean()
                pv_mesh.compute_normals(point_normals=True, split_vertices=True, feature_angle=30.0, inplace=True)
            except: continue

            mat = str(segment.material).lower()
            color, opacity = default_color, 1.0
            
            # Thiết lập độ nhám và tính kim loại dựa trên vật liệu
            metallic, roughness = 0.0, 0.5
            if "iron" in mat or "steel" in mat:
                color, metallic, roughness = iron_color, 0.9, 0.3
            elif "magnet" in mat:
                color, metallic, roughness = magnet_color, 0.6, 0.2
            elif "copper" in mat or "coil" in mat:
                color, metallic, roughness = coil_color, 0.7, 0.4
            elif "air" in mat:
                color, opacity = air_color, 0.15

            # Giữ nguyên logic thu thập thông tin hiển thị của bạn
            attrs = [a for a in dir(segment) if not a.startswith('__') and not callable(getattr(segment, a))]
            priority = ['material', 'index', 'r_length', 't_length', 'z_length']
            attrs.sort(key=lambda x: (0 if x in priority else 1, x))
            
            info_lines = [f"{'ATTRIBUTE':<22} : {'VALUE'}", "-" * 45]
            for attr in attrs:
                if attr == 'mesh': continue
                val = getattr(segment, attr)
                val_str = f"{val:.4f}" if isinstance(val, float) else str(val)
                info_lines.append(f"{attr:<22} : {val_str}")
            pv_mesh.field_data["info"] = ["\n".join(info_lines)]
            
            # Rendering: Sử dụng PBR để tạo hiệu ứng kim loại thật hơn
            actor = pl.add_mesh(pv_mesh, color=color, opacity=opacity, 
                                lighting=True, pbr=True, metallic=metallic, 
                                roughness=roughness, smooth_shading=True, pickable=True)
            
            pv_mesh._actor_ref = actor
            pv_mesh._original_color = actor.prop.color 

        def on_pick(mesh):
            if mesh is None or not hasattr(mesh, '_actor_ref'): return
            last_mesh = selection_state['last_mesh']
            if last_mesh is mesh:
                mesh._actor_ref.prop.color = getattr(mesh, '_original_color')
                selection_state['last_mesh'] = None
                return
            if last_mesh is not None: last_mesh._actor_ref.prop.color = getattr(last_mesh, '_original_color')
            mesh._actor_ref.prop.color = highlight_color
            selection_state['last_mesh'] = mesh
            if "info" in mesh.field_data:
                pl.add_text(f"== SELECTED SEGMENT ==\n{mesh.field_data['info'][0]}", 
                            position='upper_left', font_size=10, color='black', name='hud_info', font='courier')

        # Sửa lỗi Picking tranh chấp
        try:
            pl.disable_picking()
            pl.enable_mesh_picking(on_pick, show=False, show_message=False)
        except: pass

        if own_plotter:
            pl.add_text("AXIAL FLUX MOTOR SIMULATION", position='upper_right', font_size=10, color='black')
            pl.add_axes(interactive=False, line_width=2, color='black')
            pl.view_isometric()
            pl.show()
            
        return pl