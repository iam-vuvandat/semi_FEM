import numpy as np
import pyvista as pv
import ctypes

# Thiết lập DPI Awareness để giao diện sắc nét trên màn hình Surface
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

class Geometry:
    def __init__(self, geometry=None):
        """
        Khởi tạo đối tượng quản lý hình học.
        Dữ liệu geometry là danh sách các segment (Stator, Rotor, Coils, Magnets).
        """
        self.geometry = geometry if geometry is not None else []

    def show(self, plotter=None, iron_color="#D3D3D3", magnet_color="#3498DB", 
             coil_color="#E67E22", air_color="#E0F7FA", default_color="#3498DB", 
             highlight_color="#FF00FF", show_axes=True):
        """
        Phương thức hiển thị hình học tối ưu hóa hiệu năng.
        - Bỏ custom arrows.
        - Sửa lỗi 'Picking already enabled'.
        - Ưu tiên FPS khi xoay mô hình trên Surface.
        """
        
        if not self.geometry:
            print("Geometry is empty.")
            return

        # 1. Thiết lập Plotter
        pv.set_plot_theme("document")
        if plotter is None:
            pl = pv.Plotter()
            pl.set_background("white")
            own_plotter = True
        else:
            pl = plotter
            own_plotter = False

        # 2. GIẢI QUYẾT LỖI PICKING: Vô hiệu hóa mọi bộ chọn cũ trước khi vẽ lại
        try:
            pl.disable_picking()
        except:
            pass

        # 3. CẤU HÌNH ĐỒ HỌA NHẸ (Bỏ Shadows/PBR để tăng hiệu năng)
        # Sử dụng Eye Dome Lighting (EDL) - cực kỳ nhẹ nhưng giúp nhìn rõ các hốc rãnh
        pl.enable_eye_dome_lighting() 

        selection_state = {'last_mesh': None}

        # 4. VẼ CÁC THÀNH PHẦN HÌNH HỌC
        for segment in self.geometry:
            mesh_data = segment.mesh
            if mesh_data is None: 
                continue

            # Sử dụng trực tiếp mesh, bỏ qua các bước .clean() tốn CPU
            try:
                pv_mesh = pv.wrap(mesh_data)
            except: 
                continue

            # Xác định màu sắc và độ trong suốt dựa trên vật liệu
            mat = str(segment.material).lower()
            color, opacity = default_color, 1.0
            
            if "iron" in mat or "steel" in mat:
                color = iron_color
            elif "magnet" in mat:
                color = magnet_color
            elif "copper" in mat or "coil" in mat:
                color = coil_color
            elif "air" in mat:
                color, opacity = air_color, 0.10 # Air để rất mờ để không gây nhiễu

            # Lưu thông tin mô tả vào field_data (rất nhẹ, không tốn RAM)
            info = f"Material: {segment.material}\nSegment ID: {getattr(segment, 'index', 'N/A')}"
            pv_mesh.field_data["info"] = [info]
            
            # Rendering: Sử dụng Gouraud Shading tiêu chuẩn (nhanh hơn PBR gấp nhiều lần)
            actor = pl.add_mesh(
                pv_mesh, 
                color=color, 
                opacity=opacity, 
                lighting=True,
                smooth_shading=True, 
                pickable=True,
                show_edges=False # Tắt cạnh để giảm số lượng đường kẻ (Lines) cần vẽ
            )
            
            # Lưu tham chiếu phục vụ logic Picking
            pv_mesh._actor_ref = actor
            pv_mesh._original_color = actor.prop.color 

        # 5. LOGIC CHỌN ĐỐI TƯỢNG (PICKING)
        def on_pick(mesh):
            if mesh is None or not hasattr(mesh, '_actor_ref'): 
                return
            
            last_mesh = selection_state['last_mesh']
            
            # Reset màu nếu nhấn lại đối tượng cũ
            if last_mesh is mesh:
                mesh._actor_ref.prop.color = getattr(mesh, '_original_color')
                selection_state['last_mesh'] = None
                pl.remove_actor('hud_info')
                return
                
            # Đổi màu Highlight cho đối tượng mới
            if last_mesh is not None: 
                last_mesh._actor_ref.prop.color = getattr(last_mesh, '_original_color')
            
            mesh._actor_ref.prop.color = highlight_color
            selection_state['last_mesh'] = mesh
            
            # Hiển thị nhãn thông tin ở góc màn hình
            if "info" in mesh.field_data:
                pl.add_text(
                    f"Selected: {mesh.field_data['info'][0]}", 
                    position='lower_left', 
                    font_size=9, 
                    color='black', 
                    name='hud_info'
                )

        # Kích hoạt bộ chọn Mesh
        pl.enable_mesh_picking(callback=on_pick, show=False, show_message=False)

        # 6. TRỤC TỌA ĐỘ VÀ GÓC NHÌN
        if show_axes:
            # Sử dụng bộ trục tọa độ mặc định của PyVista (Xử lý bằng Shader nên cực nhanh)
            pl.add_axes(line_width=2)

        if own_plotter:
            pl.view_isometric()
            pl.show()
            
        return pl