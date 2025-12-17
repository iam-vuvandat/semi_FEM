import numpy as np
import pyvista as pv

class CylindricalMesh:
    def __init__(self, r_nodes=None, theta_nodes=None, z_nodes=None, periodic_boundary=True):
        """
        Khởi tạo lưới tọa độ trụ với 3 mảng đầu vào riêng biệt.

        Args:
            r_nodes (array-like): Mảng tọa độ các điểm chia theo bán kính (mm hoặc m).
            theta_nodes (array-like): Mảng tọa độ các điểm chia theo góc (radian).
            z_nodes (array-like): Mảng tọa độ các điểm chia theo trục dọc (mm hoặc m).
            periodic_boundary (bool): Cờ đánh dấu biên tuần hoàn (dùng cho trục theta).
        """
        # 1. Xử lý input mặc định
        if r_nodes is None: r_nodes = np.linspace(0, 1, 2)
        if theta_nodes is None: theta_nodes = np.linspace(0, np.pi, 2)
        if z_nodes is None: z_nodes = np.linspace(0, 1, 2)

        # 2. Lưu trữ các node biên
        self.r_nodes = np.array(r_nodes)
        self.theta_nodes = np.array(theta_nodes)
        self.z_nodes = np.array(z_nodes)
        
        self.periodic_boundary = periodic_boundary

        # 3. Tính số lượng node
        self.nr = len(self.r_nodes)
        self.nt = len(self.theta_nodes)
        self.nz = len(self.z_nodes)
        
        # 4. Tính số lượng phần tử (Cells)
        self.n_cells_r = max(1, self.nr - 1)
        self.n_cells_t = max(1, self.nt - 1)
        self.n_cells_z = max(1, self.nz - 1)
        
        self.total_cells = self.n_cells_r * self.n_cells_t * self.n_cells_z
        
        # 5. Tạo lưới 3D (Meshgrid)
        self.R, self.Theta, self.Z = np.meshgrid(self.r_nodes, 
                                                 self.theta_nodes, 
                                                 self.z_nodes, 
                                                 indexing='ij')

        # 6. Chuyển đổi sang tọa độ Descartes
        self.X = self.R * np.cos(self.Theta)
        self.Y = self.R * np.sin(self.Theta)

    def get_cell_centers(self):
        """Trả về tọa độ tâm (r, theta, z) của các phần tử."""
        r_c = (self.r_nodes[:-1] + self.r_nodes[1:]) / 2
        t_c = (self.theta_nodes[:-1] + self.theta_nodes[1:]) / 2
        z_c = (self.z_nodes[:-1] + self.z_nodes[1:]) / 2
        R_c, T_c, Z_c = np.meshgrid(r_c, t_c, z_c, indexing='ij')
        return R_c, T_c, Z_c

    def get_cell_volumes(self):
        """Tính thể tích vi phân dV = r * dr * dtheta * dz"""
        dr = np.diff(self.r_nodes)
        dtheta = np.diff(self.theta_nodes)
        dz = np.diff(self.z_nodes)
        r_c = (self.r_nodes[:-1] + self.r_nodes[1:]) / 2
        
        DR, DTHETA, DZ = np.meshgrid(dr, dtheta, dz, indexing='ij')
        R_C, _, _ = np.meshgrid(r_c, dtheta, dz, indexing='ij')
        
        return R_C * DR * DTHETA * DZ

    def to_pyvista_grid(self):
        """Xuất sang đối tượng pyvista.StructuredGrid."""
        grid = pv.StructuredGrid(self.X, self.Y, self.Z)
        try:
            vols = self.get_cell_volumes().flatten(order='F')
            grid.cell_data["Volume"] = vols
        except Exception as e:
            print(f"Warning: Could not compute volumes: {e}")
        return grid

    def show(self, 
             show_edges=True, 
             notebook=False, 
             plotter=None,      # Hỗ trợ gộp Plotter
             opacity=0.3):      # Độ trong suốt (để nhìn xuyên qua khi vẽ chồng)
        """
        Hiển thị lưới 3D sử dụng PyVista.
        Hỗ trợ vẽ độc lập hoặc vẽ chồng lên Geometry.
        """
        # --- 1. XÁC ĐỊNH PLOTTER ---
        if plotter is None:
            pv.set_plot_theme("dark")
            pl = pv.Plotter(notebook=notebook, window_size=[1200, 900])
            pl.set_background("#1A1A1A") 
            pl.add_axes()
            own_plotter = True
            # Nếu chạy độc lập, tăng opacity lên để nhìn rõ hơn
            if opacity == 0.3: opacity = 0.85 
        else:
            pl = plotter
            own_plotter = False

        # --- 2. CHUẨN BỊ DỮ LIỆU ---
        grid = self.to_pyvista_grid()

        # --- 3. VẼ MESH ---
        pl.add_mesh(grid, 
                    show_edges=show_edges,
                    scalars="Volume", 
                    cmap="viridis", 
                    opacity=opacity,
                    edge_color="#555555", # Màu cạnh xám vừa phải
                    scalar_bar_args={"title": "Cell Volume"})
        
        # --- 4. HIỂN THỊ THÔNG TIN ---
        # Chỉ hiện Grid Box nếu tự vẽ (để tránh rác hình khi gộp)
        if own_plotter:
            pl.show_grid(color='gray', font_size=10, grid=False, location='outer')

        stats_text = (f"== MESH STATISTICS ==\n"
                      f"R nodes : {self.nr}\n"
                      f"T nodes : {self.nt}\n"
                      f"Z nodes : {self.nz}\n"
                      f"Total Cells: {self.total_cells}")
        
        # Đặt ở góc dưới trái để tránh đè lên thông tin Geometry (thường ở trên trái)
        pl.add_text(stats_text, position='lower_left', font_size=10, font='courier', color='#CCCCCC')

        # --- 5. SHOW ---
        if own_plotter:
            pl.view_isometric()
            pl.show()
            
        return pl

# --- PHẦN CHẠY THỬ (TEST) ---
if __name__ == "__main__":
    print("Initializing Cylindrical Mesh...")
    r_arr = np.linspace(50, 80, 10)
    theta_arr = np.linspace(0, np.pi, 30)
    z_arr = np.linspace(0, 100, 5)
    
    mesh = CylindricalMesh(r_nodes=r_arr, theta_nodes=theta_arr, z_nodes=z_arr)
    print(f"Mesh shape: {mesh.R.shape}")
    
    # Test chạy độc lập
    print("Displaying PyVista window...")
    mesh.show()