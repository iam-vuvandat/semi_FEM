from typing import Any
import numpy as np
import dataclasses

@dataclasses.dataclass
class ValueAccess:
    value: Any
    valid: Any
    flat_index: Any

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
        self.global_size = None

        if reluctance_network is not None:

            self.nr = int(reluctance_network.mesh.n_cells_r)
            self.nt = int(reluctance_network.mesh.n_cells_t)
            self.nz = int(reluctance_network.mesh.n_cells_z)

            self.total_size = (2 * self.nr * self.nt * self.nz) - (self.nt * self.nz) - (self.nr * self.nt) + 1 
            
            self.Ort_size = ((self.nr - 1) , self.nt, self.nz,(self.nr - 1) * self.nt, self.nz * (self.nr - 1) * self.nt  )
            self.Orz_size = (self.nr - 1 , self.nz -1, self.nt,(self.nr - 1) * (self.nz -1), self.nt * (self.nr - 1) * (self.nz -1)  )
            self.Otz_size = (self.nt , self.nz -1, 1, (self.nt)*(self.nz -1),1 * (self.nt)*(self.nz -1) )
            self.global_size = 1
        
            if self.data is None:
                self.data = np.zeros(self.total_size)

    def access_Ort_plane(self,
                         z_layer,
                         position):
        # position = (r_idex, theta_index)
        
        value = 0.0
        valid = False
        flat_index = None
        begin_index = 0 

        if z_layer < 0 or z_layer >= self.Ort_size[2]:
            pass
        else:
            if  position[0] < 0 or position[0] >= self.Ort_size[0]:
                pass
            else:
                t_index = position[1] % self.Ort_size[1]
                # quy ước tốc độ tăng trong mảng: r>t>z

                flat_index = begin_index + self.Ort_size[3] * z_layer + t_index * self.Ort_size[0] + position[0]
                value = self.data[flat_index]
                valid = True

        return ValueAccess(value=value, valid=valid, flat_index=flat_index)
                
    def access_Orz_plane(self,
                         t_layer,
                         position):
        # position = (r_index, z_index)
        # quy ước tốc độ tăng trong mảng r>z>t
        value = 0.0
        valid = False
        flat_index = None
        begin_index = self.Ort_size[4]
        
        t_layer_access = t_layer % self.nt

        if position[0] < 0 or position[1] < 0:
            pass
        else:
            if position[0] >= self.Orz_size[0] or position[1] >= self.Orz_size[1]:
                pass
            else:
                # r > z > t
                flat_index = begin_index + t_layer_access * self.Orz_size[3] + position[1] * self.Orz_size[0] + position[0]
                value = self.data[flat_index]
                valid = True
                
        return ValueAccess(value=value, valid=valid, flat_index=flat_index)
    
    def access_Otz_plane(self,
                         r_layer,
                         position):
        
        # position = (t_index, z_index)
        # thứ tự tăng trong mảng: t>z>r
        
        value = 0.0
        valid = False
        flat_index = None
        begin_index = self.Ort_size[4] + self.Orz_size[4]

        if r_layer < 0 or r_layer >= self.Otz_size[2]:
            pass 
        else:
            if position[1] < 0 or position[1] >= self.Otz_size[1]:
                pass
            else:
                t_index = position[0] % self.Otz_size[0]
                # t > z > r
                flat_index = begin_index + r_layer * self.Otz_size[3] + position[1] * self.Otz_size[0] + t_index
                value = self.data[flat_index]
                valid = True

        return ValueAccess(value=value, valid=valid, flat_index=flat_index)
    
    def access_global(self,
                      position):
        
        # position = (r_index,z_index)
        # quy ước biến vòng global xếp cuối cùng
        # biến global chỉ nằm ở r_index = 0; z_index = 0 
        value = 0.0
        valid = False
        flat_index = None
        begin_index = self.Ort_size[4] + self.Orz_size[4] + self.Otz_size[4]

        if position[0] == 0:
            if position[1] == 0 : 
                flat_index = begin_index
                value = self.data[flat_index]
                valid = True

        return ValueAccess(value=value, valid=valid, flat_index=flat_index)

