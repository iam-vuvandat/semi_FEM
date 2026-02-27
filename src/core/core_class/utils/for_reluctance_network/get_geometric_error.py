import numpy as np

def get_geometric_error(reluctance_network):
    object_geometry = reluctance_network.geometry
    geometry_list = object_geometry.geometry

    original_solid_volume = 0.0
    for segment in geometry_list:
        if segment.material == "air":
            pass
        else:
            original_solid_volume += segment.volume

    total_vollume_error = 0.0
    elements_list = reluctance_network.elements.flatten()

    for element in elements_list:
        total_vollume_error += element.volume_error

    if reluctance_network.mesh.periodic_boundary == True:
        total_vollume_error *= reluctance_network.symmetry_factor

    return np.abs(total_vollume_error/original_solid_volume)
