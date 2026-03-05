import numpy as np
import pyvista as pv

class CylindricalMesh:
    def __init__(self, r_nodes=None, theta_nodes=None, z_nodes=None, periodic_boundary=True, adaptive_mesh_data = None):
        """
        Khởi tạo lưới hình trụ phục vụ mô phỏng máy điện.
        Tự động tạo lưới tọa độ X, Y, Z từ các nút Cylindrical.
        """
        if r_nodes is None: r_nodes = np.linspace(0, 1, 2)
        if theta_nodes is None: theta_nodes = np.linspace(0, np.pi, 2)
        if z_nodes is None: z_nodes = np.linspace(0, 1, 2)

        self.r_nodes = np.array(r_nodes)
        self.theta_nodes = np.array(theta_nodes)
        self.delta_theta = np.abs(self.theta_nodes[5] - self.theta_nodes[4])
        self.z_nodes = np.array(z_nodes)
        self.periodic_boundary = periodic_boundary

        self.nr = len(self.r_nodes)
        self.nt = len(self.theta_nodes)
        self.nz = len(self.z_nodes)
        
        self.n_cells_r = max(1, self.nr - 1)
        self.n_cells_t = max(1, self.nt - 1)
        self.n_cells_z = max(1, self.nz - 1)
        self.total_cells = self.n_cells_r * self.n_cells_t * self.n_cells_z
        
        # Tạo lưới tọa độ Cartesian (X, Y, Z) để PyVista có thể hiểu
        self.R, self.Theta, self.Z = np.meshgrid(self.r_nodes, self.theta_nodes, self.z_nodes, indexing='ij')
        self.X = self.R * np.cos(self.Theta)
        self.Y = self.R * np.sin(self.Theta)
        self.adaptive_mesh_data = adaptive_mesh_data

    def get_cell_centers(self):
        """Tính toán tọa độ tâm của từng cell trong lưới."""
        r_c = (self.r_nodes[:-1] + self.r_nodes[1:]) / 2
        t_c = (self.theta_nodes[:-1] + self.theta_nodes[1:]) / 2
        z_c = (self.z_nodes[:-1] + self.z_nodes[1:]) / 2
        return np.meshgrid(r_c, t_c, z_c, indexing='ij')

    def to_pyvista_grid(self):
        """Chuyển đổi dữ liệu sang StructuredGrid."""
        return pv.StructuredGrid(self.X, self.Y, self.Z)

    def show(self, show_edges=True, notebook=False, plotter=None, opacity=1.0, save_path=None):
        """
        Hiển thị lưới ở chế độ Đặc (Opaque):
        - Bề mặt: Xám 50% (#808080).
        - Cạnh: Đen (Black).
        - Độ phân giải: MSAA 8x để nét vẽ sắc sảo trên Surface.
        """
        # Sử dụng theme Document để có nền trắng sạch sẽ
        pv.set_plot_theme("document")
        
        if plotter is None:
            pl = pv.Plotter(notebook=notebook, window_size=[1920, 1080])
            pl.set_background("white")
            own_plotter = True
        else:
            pl = plotter
            own_plotter = False

        # Ép khử răng cưa chất lượng cao nhất cho các đường lưới (Edges)
        try:
            pl.enable_anti_aliasing('msaa', multi_samples=8)
        except:
            pass

        grid = self.to_pyvista_grid()

        # THIẾT LẬP HIỂN THỊ ĐẶC (OPAQUE):
        # opacity=1.0: Hoàn toàn không trong suốt.
        # color="#808080": Màu xám trung tính (50%).
        # edge_color="black": Nét vẽ đen sắc nét.
        pl.add_mesh(grid, 
                    show_edges=show_edges,
                    color="#808080", 
                    opacity=1.0,       # Thiết lập đặc 100%
                    edge_color="black",
                    line_width=1.5,
                    smooth_shading=True,
                    specular=0.2,      # Phản xạ nhẹ để nhìn rõ khối
                    pickable=True)
        
        if own_plotter:
            pl.view_isometric()
            if save_path:
                pl.screenshot(save_path, scale=4)
            pl.show()
            
        return pl

if __name__ == "__main__":
    # Test hiển thị lưới ở chế độ Đặc - Xám - Nét Đen
    r_arr = np.linspace(50, 100, 15)
    theta_arr = np.linspace(0, np.pi, 35)
    z_arr = np.linspace(0, 50, 5)
    
    mesh = CylindricalMesh(r_nodes=r_arr, theta_nodes=theta_arr, z_nodes=z_arr)
    mesh.show()