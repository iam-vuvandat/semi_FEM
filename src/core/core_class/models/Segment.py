import numpy as np 

class Segment:
    def __init__(self,
                 mesh=None,
                 material="air",
                 magnet_source=0.0,
                 magnetization_direction=np.array([0., 0., 1.]),
                 winding_vector=np.array([0., 0., 0.]),
                 winding_normal=np.array([0., 0., 1.]),
                 dimension=np.array([0., 0., 0.])): 
        
        self.mesh = mesh
        self.material = material
        self.magnet_source = float(magnet_source)
        
        self.magnetization_direction = np.array(magnetization_direction, dtype=float)
        self.winding_vector = np.array(winding_vector, dtype=float)
        self.winding_normal = np.array(winding_normal, dtype=float)

        if dimension is None:
            self.dimension = np.array([0., 0., 0.], dtype=float)
        else:
            self.dimension = np.array(dimension, dtype=float)
            
            if self.dimension.size != 3:
                raise ValueError("Dimension phải là mảng chứa 3 phần tử [r, theta, z]")

    def __repr__(self):
        return (f"Segment(mat='{self.material}', "
                f"dim={self.dimension})")

if __name__ == "__main__":
    input_dim = [0.005, np.pi/6, 0.1]
    
    seg = Segment(material="NDFeB", 
                  magnet_source=1.2,
                  dimension=input_dim)

    print("Thông tin Segment:")
    print(seg)
    print(f"Dimension Array: {seg.dimension}")
    print(f"Type: {type(seg.dimension)}")