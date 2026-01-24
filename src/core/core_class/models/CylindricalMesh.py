import numpy as np
import pyvista as pv

class CylindricalMesh:
    def __init__(self, r_nodes=None, theta_nodes=None, z_nodes=None, periodic_boundary=True, adaptive_mesh_data = None):
        if r_nodes is None: r_nodes = np.linspace(0, 1, 2)
        if theta_nodes is None: theta_nodes = np.linspace(0, np.pi, 2)
        if z_nodes is None: z_nodes = np.linspace(0, 1, 2)

        self.r_nodes = np.array(r_nodes)
        self.theta_nodes = np.array(theta_nodes)
        self.delta_theta = np.abs(self.theta_nodes[1] - self.theta_nodes[0])
        self.z_nodes = np.array(z_nodes)
        self.periodic_boundary = periodic_boundary

        self.nr = len(self.r_nodes)
        self.nt = len(self.theta_nodes)
        self.nz = len(self.z_nodes)
        
        self.n_cells_r = max(1, self.nr - 1)
        self.n_cells_t = max(1, self.nt - 1)
        self.n_cells_z = max(1, self.nz - 1)
        self.total_cells = self.n_cells_r * self.n_cells_t * self.n_cells_z
        
        self.R, self.Theta, self.Z = np.meshgrid(self.r_nodes, self.theta_nodes, self.z_nodes, indexing='ij')
        self.X = self.R * np.cos(self.Theta)
        self.Y = self.R * np.sin(self.Theta)
        self.adaptive_mesh_data = adaptive_mesh_data

    def get_cell_centers(self):
        r_c = (self.r_nodes[:-1] + self.r_nodes[1:]) / 2
        t_c = (self.theta_nodes[:-1] + self.theta_nodes[1:]) / 2
        z_c = (self.z_nodes[:-1] + self.z_nodes[1:]) / 2
        return np.meshgrid(r_c, t_c, z_c, indexing='ij')

    def to_pyvista_grid(self):
        return pv.StructuredGrid(self.X, self.Y, self.Z)

    def show(self, show_edges=True, notebook=False, plotter=None, opacity=0.3, save_path=None):
        pv.set_plot_theme("document")
        
        if plotter is None:
            pl = pv.Plotter(notebook=notebook, window_size=[1600, 1200])
            pl.set_background("white")
            pl.enable_anti_aliasing('msaa')
            own_plotter = True
        else:
            pl = plotter
            own_plotter = False

        grid = self.to_pyvista_grid()

        pl.add_mesh(grid, 
                    show_edges=show_edges,
                    color="white",
                    opacity=opacity,
                    edge_color="black",
                    line_width=1.5)
        
        if own_plotter:
            pl.view_isometric()
            if save_path:
                pl.screenshot(save_path, scale=4)
            pl.show()
            
        return pl

if __name__ == "__main__":
    r_arr = np.linspace(50, 80, 10)
    theta_arr = np.linspace(0, np.pi, 30)
    z_arr = np.linspace(0, 100, 5)
    
    mesh = CylindricalMesh(r_nodes=r_arr, theta_nodes=theta_arr, z_nodes=z_arr)
    mesh.show()