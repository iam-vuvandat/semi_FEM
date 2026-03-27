import trimesh
import numpy as np

def create_tube(inner_radius, outer_radius, height, z_offset=0.0, sections=360):
    if inner_radius >= outer_radius:
        raise ValueError("Bán kính ngoài phải lớn hơn bán kính trong.")

    cylinder_outer = trimesh.creation.cylinder(radius=outer_radius, height=height, sections=sections)
    cylinder_inner = trimesh.creation.cylinder(radius=inner_radius, height=height + 0.2, sections=sections)

    # Trong trimesh 4.x, neu manifold3d da cai, 'manifold' se la engine mac dinh manh nhat
    mesh = trimesh.boolean.difference([cylinder_outer, cylinder_inner], engine='manifold')

    matrix = trimesh.transformations.translation_matrix([0, 0, height/2.0 + z_offset])
    mesh.apply_transform(matrix)

    return mesh