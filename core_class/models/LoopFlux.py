import numpy as np

class LoopFLux:
    def __init__(self,
                 data = None,
                 reluctance_network = None):
        
        self.data = data
        
        self.nr = None
        self.nt = None
        self.nz = None
        self.total_size = None

        self.Ort_size = None
        self.Orz_size = None
        self.Otz_size = None

        if reluctance_network is not None:

            self.nr = int(reluctance_network.mesh.n_cells_r)
            self.nt = int(reluctance_network.mesh.n_cells_t)
            self.nz = int(reluctance_network.mesh.n_cells_z)

            self.total_size = (2 * self.nr * self.nt * self.nz) - (self.nt * self.nz) - (self.nr * self.nt) + 1 
            
            self.Ort_size = ((self.nr - 1) , self.nt, self.nz,(self.nr - 1) * self.nt  )
            self.Orz_size = (self.nr - 1 , self.nz -1, self.nt,(self.nr - 1) * (self.nz -1) )
            self.Otz_size = (self.nt , self.nz -1, 1, (self.nt)*(self.nz -1))

            if self.data is None:
                self.data = np.zeros(self.total_size)

    def access_Ort_plane(self,
                         z_layer,
                         position):
        # position = (r_idex, theta_index)
        
        value = 0.0
        begin_index = 0 
        if z_layer < 0 or z_layer >= self.Ort_size[2]:
            pass
        else:
            if  position[0] <0 or position[0] >= self.Ort_size[0]:
                pass
            else:
                t_index = position[1] % self.Ort_size[1]
                # quy ước tốc độ tăng trong mảng: r>t>z

                value = self.data[begin_index + self.Ort_size[3] * z_layer + t_index*self.Ort_size[0] +position[0]  ]

        return value
                
        
    