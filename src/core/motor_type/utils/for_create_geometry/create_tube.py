import numpy as np
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def create_tube(inner_radius, outer_radius, height, z_offset=0.0, sections=360):
    if inner_radius >= outer_radius:
        raise ValueError("Bán kính ngoài phải lớn hơn bán kính trong.")

    cylinder_outer = trimesh.creation.cylinder(radius=outer_radius, height=height, sections=sections)
    cylinder_inner = trimesh.creation.cylinder(radius=inner_radius, height=height + 0.1, sections=sections)

    # Su dung manifold engine de fix loi No backends available
    mesh = trimesh.boolean.difference([cylinder_outer, cylinder_inner], engine='manifold')

    matrix = trimesh.transformations.translation_matrix([0, 0, height/2.0 + z_offset])
    mesh.apply_transform(matrix)

    return mesh

def plot_mesh_matplotlib(mesh, title="3D Tube"):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    polygons = mesh.vertices[mesh.faces]
    mesh_collection = Poly3DCollection(polygons, alpha=0.7, edgecolor='k', linewidths=0.1)
    mesh_collection.set_facecolor((0.2, 0.6, 1.0))
    ax.add_collection3d(mesh_collection)

    # Dinh nghia min_limits va max_limits tu bounds cua mesh
    min_limits = mesh.bounds[0]
    max_limits = mesh.bounds[1]

    max_range = (max_limits - min_limits).max() / 2.0
    mid_x = (max_limits[0] + min_limits[0]) * 0.5
    mid_y = (max_limits[1] + min_limits[1]) * 0.5
    mid_z = (max_limits[2] + min_limits[2]) * 0.5

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)

    plt.show()

if __name__ == "__main__":
    try:
        my_tube = create_tube(inner_radius=3, outer_radius=5, height=10, z_offset=2, sections=40)
        plot_mesh_matplotlib(my_tube, title="Hình trụ rỗng (Matplotlib)")
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")