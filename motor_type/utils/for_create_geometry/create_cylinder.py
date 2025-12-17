import trimesh
import numpy as np



def create_cylinder(radius, height, z_offset=0.0, sections=360):
    """
    Tạo hình trụ với đáy nằm tại độ cao z_offset.
    """
    # 1. Tạo hình trụ (Mặc định tâm tại 0,0,0)
    mesh = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    
    # 2. Dịch chuyển để đáy nằm tại z_offset
    # (Mặc định đáy đang ở -height/2, cần cộng thêm height/2 để về 0, rồi cộng z_offset)
    matrix = trimesh.transformations.translation_matrix([0, 0, height/2.0 + z_offset])
    mesh.apply_transform(matrix)
    
    return mesh