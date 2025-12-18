from motor_type.utils.for_axial_flux_motor_type_1.find_symmetry_factor import find_symmetry_factor
from motor_type.utils.for_axial_flux_motor_type_1.find_winding_matrix import find_winding_matrix
from material.models.MaterialDataBase import MaterialDataBase
from motor_type.utils.for_axial_flux_motor_type_1.create_geometry import create_geometry
from core_class.models.ReluctanceNetwork import ReluctanceNetwork
from motor_type.utils.for_axial_flux_motor_type_1.create_adaptive_mesh import create_adaptive_mesh
import pyvista as pv
import math
pi = math.pi

# Init Axial Flux Motor : single stator, single rotor, parallel slot, surface mount magnet, surface radial
class AxialFluxMotorType1:
    def __init__(self,
                 # radial_stator_parameter
                 slot_number = 15,
                 stator_lam_dia = 150 * 1e-3,
                 stator_bore_dia = 50 * 1e-3,
                 slot_opening = 5 * 1e-3,
                 wdg_extension_inner = 0,
                 wdg_extension_outer = 0,
                 # radial_rotor_parameter
                 pole_number = 10,
                 rotor_lam_dia = 150 * 1e-3,
                 magnet_arc = 140,
                 magnet_embed_depth = 5 * 1e-3, 
                 magnet_depth = 40 * 1e-3,
                 magnet_segments = 1,
                 banding_depth = 0 * 1e-3,
                 shaft_dia = 0 * 1e-3,
                 shaft_hole_diameter = 50 * 1e-3,
                 # linear_stator_parameter 
                 slot_width = 10 * 1e-3,
                 slot_depth = 15 * 1e-3,
                 slot_corner_radius = 0, # deg
                 tooth_tip_depth = 2 * 1e-3,
                 tooth_tip_angle = 30, # deg
                 stator_length = 27 * 1e-3,
                 # linear_rotor_parameter 
                 airgap = 2 * 1e-3,
                 magnet_length = 4 * 1e-3,    
                 rotor_length = 8 * 1e-3,    
                 # winding  
                 phase = 3,
                 turns = 50,
                 throw = 1,
                 parallel_path = 1,
                 winding_layer = 2,
                 winding_type = "concentrated",
                 winding_matrix = None,
                 # Material
                 air = "default",
                 magnet_type = "N30UH",
                 iron_type = "M350-50A"
                 ):
        
        # --- Gán Radial Stator Parameters ---
        self.slot_number = slot_number
        self.stator_lam_dia = stator_lam_dia
        self.stator_bore_dia = stator_bore_dia
        self.slot_opening = slot_opening
        self.wdg_extension_inner = wdg_extension_inner
        self.wdg_extension_outer = wdg_extension_outer

        # --- Gán Radial Rotor Parameters ---
        self.pole_number = pole_number
        self.rotor_lam_dia = rotor_lam_dia
        self.magnet_arc = magnet_arc
        self.magnet_embed_depth = magnet_embed_depth
        self.magnet_depth = magnet_depth
        self.magnet_segments = magnet_segments
        self.banding_depth = banding_depth
        self.shaft_dia = shaft_dia
        self.shaft_hole_diameter = shaft_hole_diameter

        # --- Gán Linear Stator Parameters ---
        self.slot_width = slot_width
        self.slot_depth = slot_depth
        self.slot_corner_radius = slot_corner_radius
        self.tooth_tip_depth = tooth_tip_depth
        self.tooth_tip_angle = tooth_tip_angle
        self.stator_length = stator_length

        # --- Gán Linear Rotor Parameters ---
        self.airgap = airgap
        self.magnet_length = magnet_length
        self.rotor_length = rotor_length

        # --- Gán Winding Parameters ---
        self.phase = phase
        self.turns = turns
        self.throw = throw
        self.parallel_path = parallel_path
        self.winding_layer = winding_layer
        self.winding_type = winding_type
        self.winding_matrix = winding_matrix

        # Hệ số tuần hoàn 
        symmetry_data = find_symmetry_factor(self)
        self.symmetry_factor = symmetry_data.symmetry_factor

        # Ma trận dây quấn
        winding_data = find_winding_matrix(self)
        self.winding_matrix = winding_data.winding_matrix

        # Vật liệu 
        self.material_database = MaterialDataBase(air=air,
                                                  magnet_type= magnet_type,
                                                  iron_type= iron_type)
        self.geometry = None
        self.mesh     = None
        self.reluctance_network = None

    def create_geometry(self,
                        rotor_angle_offset = 0,
                        stator_angle_offset = 0,
                        create_rotor_yoke = True,
                        create_magnet = True,
                        create_tooth = True,
                        create_stator_yoke = True):
        
        self.geometry = create_geometry(motor=self,
                                        rotor_angle_offset=rotor_angle_offset,
                                        stator_angle_offset=stator_angle_offset,
                                        create_rotor_yoke=create_rotor_yoke,
                                        create_magnet=create_magnet,
                                        create_tooth=create_tooth,
                                        create_stator_yoke=create_stator_yoke)

    def create_adaptive_mesh(self,
                         n_r_in                       =2,
                         n_r_1                        =5,
                         n_r_2                        =8,
                         n_r_3                        =5,
                         n_r_out                      =2,
                         n_theta                      =90,
                         n_z_in_air                   =2,
                         n_z_rotor_yoke               =3,
                         n_z_magnet                   =2,
                         n_z_airgap                   =3,
                         n_z_tooth_tip_1              =2,
                         n_z_tooth_tip_2              =3,
                         n_z_tooth_body               =4,
                         n_z_stator_yoke              =4,
                         n_z_out_air                  =2,
                         use_symmetry_factor=True,
                         periodic_boundary=True):
        """
        Tạo lưới thích ứng (Adaptive Mesh) cho động cơ.
        Các tham số đầu vào sẽ ghi đè lên giá trị mặc định.
        """
        # Gọi hàm tạo lưới và truyền đúng các biến số vào (không hardcode số)
        self.mesh = create_adaptive_mesh(
            motor=self,
            n_r_in=n_r_in,
            n_r_1=n_r_1,
            n_r_2=n_r_2,
            n_r_3=n_r_3,
            n_r_out=n_r_out,
            n_theta=n_theta,
            n_z_in_air=n_z_in_air,
            n_z_rotor_yoke=n_z_rotor_yoke,
            n_z_magnet=n_z_magnet,
            n_z_airgap=n_z_airgap,
            n_z_tooth_tip_1=n_z_tooth_tip_1,
            n_z_tooth_tip_2=n_z_tooth_tip_2,
            n_z_tooth_body=n_z_tooth_body,
            n_z_stator_yoke=n_z_stator_yoke,
            n_z_out_air=n_z_out_air,
            use_symmetry_factor=use_symmetry_factor,
            periodic_boundary=periodic_boundary
        )
        
        return self.mesh
    
    def create_reluctance_network(self):
        self.reluctance_network = ReluctanceNetwork(motor = self,
                                                    geometry=self.geometry,
                                                    mesh = self.mesh)
        
        return self.reluctance_network
    
    def show(self, show_geometry=True, show_mesh=True):
        """
        Hiển thị toàn bộ mô hình động cơ (Geometry + Mesh).
        Kết hợp tính năng tương tác (Click) của Geometry và trực quan hóa Lưới.
        """
        

        # --- 1. KHỞI TẠO SÂN KHẤU CHUNG (PLOTTER) ---
        pv.set_plot_theme("dark")
        pl = pv.Plotter(window_size=[1400, 1000])
        pl.set_background("#0F0F0F")  # Nền đen tuyền hiện đại
        pl.add_axes()
        
        # [FIX]: Sửa position='upper_center' thành 'upper_right' để tránh KeyError
        # và dùng font to hơn một chút để làm tiêu đề
        pl.add_text("AXIAL FLUX MOTOR SIMULATION", position='upper_right', font_size=10, color='white')

        # Thêm đèn chiếu sáng (Quan trọng để Geometry hiện khối 3D đẹp)
        light = pv.Light(position=(1000, 1000, 1000), color='white', intensity=0.9)
        pl.add_light(light)

        has_content = False

        # --- 2. VẼ GEOMETRY (CÁC KHỐI ĐẶC) ---
        if show_geometry:
            if hasattr(self, 'geometry') and self.geometry is not None:
                print("[INFO] Adding Geometry layer...")
                # Gọi hàm show của Geometry, truyền plotter 'pl' vào.
                # Geometry sẽ vẽ các khối lên 'pl' và gắn sự kiện click vào 'pl'.
                # Thông tin click sẽ hiện ở 'upper_left'
                self.geometry.show(plotter=pl)
                has_content = True
            else:
                print("[WARNING] Geometry data is missing. Please run 'create_geometry()' first.")

        # --- 3. VẼ MESH (LƯỚI TÍNH TOÁN) ---
        if show_mesh:
            if hasattr(self, 'mesh') and self.mesh is not None:
                print("[INFO] Adding Mesh layer...")
                # Gọi hàm show của Mesh, truyền plotter 'pl' vào.
                # Mesh sẽ tự động vẽ mờ (opacity=0.3)
                # Thông tin thống kê mesh sẽ hiện ở 'lower_left'
                self.mesh.show(plotter=pl, show_edges=True)
                has_content = True
            else:
                print("[WARNING] Mesh data is missing. Please run 'create_adaptive_mesh()' first.")

        # --- 4. HIỂN THỊ CỬA SỔ ---
        if has_content:
            print("[INFO] Displaying interactive window...")
            pl.view_isometric()
            pl.show()
        else:
            print("[ERROR] Nothing to show. Please generate Geometry or Mesh first.")