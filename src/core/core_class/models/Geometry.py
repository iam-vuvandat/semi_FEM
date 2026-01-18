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
        
        # Cấu hình thông số mũi tên
        arrow_params = {
            'tip_length': 0.1,
            'tip_radius': 0.03,
            'shaft_radius': 0.01,
            'scale': length
        }

        # 1. Trục Z (Xanh dương)
        z_arrow = pv.Arrow(start=origin, direction=[0, 0, 1], **arrow_params)
        pl.add_mesh(z_arrow, color='#2980B9', lighting=False, name='z_axis_arrow')
        
        # 2. Trục R (Đỏ)
        r_arrow = pv.Arrow(start=origin, direction=[1, 0, 0], **arrow_params)
        pl.add_mesh(r_arrow, color='#C0392B', lighting=False, name='r_axis_arrow')
        
        # 3. Trục Theta (Xanh lá)
        radius_theta = length * 0.9 
        angle_deg = 35
        angle_rad = np.deg2rad(angle_deg)
        
        p_start = [radius_theta, 0, 0]
        p_end = [radius_theta * np.cos(angle_rad), radius_theta * np.sin(angle_rad), 0]
        
        theta_arc = pv.CircularArc(pointa=p_start, pointb=p_end, center=origin)
        pl.add_mesh(theta_arc, color='#27AE60', line_width=4, name='theta_arc_line')

        # Mũi tên tiếp tuyến cho trục Theta
        tangent_dir = [-np.sin(angle_rad), np.cos(angle_rad), 0]
        theta_tip = pv.Cone(
            center=p_end,
            direction=tangent_dir,
            height=length * 0.08,
            radius=length * 0.025,
            resolution=20
        )
        pl.add_mesh(theta_tip, color='#27AE60', lighting=False, name='theta_axis_tip')

        # 4. SỬA LẠI NHÃN (Sử dụng add_point_labels để ghim vào tọa độ 3D)
        offset = length * 0.1
        
        # Tạo danh sách các điểm tọa độ 3D cho nhãn
        label_points = [
            origin - [offset*0.3, offset*0.3, 0], # Vị trí chữ O
            [0, 0, length + offset],             # Vị trí chữ z
            [length + offset, 0, 0],             # Vị trí chữ r
            [radius_theta * 1.1 * np.cos(angle_rad/2), 
             radius_theta * 1.1 * np.sin(angle_rad/2), 0] # Vị trí chữ theta
        ]
        
        # Nội dung nhãn (Nếu font hệ thống lỗi, hãy thay θ bằng 'theta')
        labels = ["O", "z", "r", "θ"]

        pl.add_point_labels(
            label_points, 
            labels,
            font_size=25,       # Kích thước chữ
            text_color='black',
            shape=None,         # Không vẽ khung bao quanh chữ
            show_points=False,   # Không vẽ điểm chấm tại tọa độ
            always_visible=True, # Nhãn luôn hiện dù bị vật thể che
            name='axis_labels'
        )
    def show(self, 
             plotter=None,             
             iron_color="#D3D3D3",    
             magnet_color="#E74C3C",  
             coil_color="#E67E22",    
             air_color="#E0F7FA",     
             default_color="#3498DB",
             highlight_color="#FF00FF",
             show_axes=True):
        
        if not self.geometry:
            print("Geometry is empty.")
            return

        pv.set_plot_theme("document")
        if plotter is None:
            pl = pv.Plotter(window_size=[1600, 1200])
            pl.set_background("white") 
            try:
                pl.enable_anti_aliasing('msaa')
            except: pass
            own_plotter = True
        else:
            pl = plotter
            own_plotter = False

        if show_axes:
            max_val = 100
            try:
                all_bounds = []
                for s in self.geometry:
                    if s.mesh is not None:
                        all_bounds.extend(pv.wrap(s.mesh).bounds)
                if all_bounds:
                    max_val = max([abs(x) for x in all_bounds])
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

            if "iron" in mat or "steel" in mat: color = iron_color
            elif "magnet" in mat: color = magnet_color
            elif "copper" in mat or "coil" in mat: color = coil_color
            elif "air" in mat: color, opacity = air_color, 0.15

            # Thu thập thông tin hiển thị
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
            
            # Rendering: Matte finish (Ambient cao, Specular triệt tiêu)
            actor = pl.add_mesh(pv_mesh, color=color, opacity=opacity, 
                                lighting=True, pbr=False, diffuse=0.7, 
                                ambient=0.4, specular=0.0, pickable=True)
            
            pv_mesh._actor_ref = actor
            pv_mesh._original_color = actor.prop.color 

        def on_pick(mesh):
            if mesh is None or not hasattr(mesh, '_actor_ref'): return
            last_mesh = selection_state['last_mesh']
            
            if last_mesh is mesh:
                mesh._actor_ref.prop.color = getattr(mesh, '_original_color')
                selection_state['last_mesh'] = None
                pl.add_text("Select a segment...", position='upper_left', font_size=10, color='black', name='hud_info')
                return

            if last_mesh is not None:
                last_mesh._actor_ref.prop.color = getattr(last_mesh, '_original_color')
            
            mesh._actor_ref.prop.color = highlight_color
            selection_state['last_mesh'] = mesh
            
            if "info" in mesh.field_data:
                pl.add_text(f"== SELECTED SEGMENT ==\n{mesh.field_data['info'][0]}", 
                            position='upper_left', font_size=10, color='black', name='hud_info', font='courier')

        pl.enable_mesh_picking(on_pick, show=False, show_message=False)

        if own_plotter:
            pl.add_text("AXIAL FLUX MOTOR SIMULATION", position='upper_right', font_size=10, color='black')
            pl.add_axes(interactive=False, line_width=2, color='black')
            pl.view_isometric()
            pl.show()
            
        return pl