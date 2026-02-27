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

    discreted_solid_volume = 0.0
    elements_list = reluctance_network.elements.flatten()

    for element in elements_list:
        if element.material =="air":
            pass
        else:
            discreted_solid_volume += element.get_volume()

    if reluctance_network.mesh.periodic_boundary == True:
        discreted_solid_volume *= reluctance_network.symmetry_factor

    return np.abs((discreted_solid_volume - original_solid_volume)/original_solid_volume)
