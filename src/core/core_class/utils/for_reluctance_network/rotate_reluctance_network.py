import numpy as np
from src.core.core_class.utils.for_element.get_neighbor_elements_position import get_neighbor_elements_position

def rotate_reluctance_network(reluctance_network, z_indices=(0, 1, 2), n_step=1):
    delta_theta = reluctance_network.mesh.delta_theta
    reluctance_network.mechanical.current_position += delta_theta * n_step
    
    if reluctance_network.vectorized_optimization is False:
        z_idx_clean = np.atleast_1d(z_indices).astype(int)
        elements = reluctance_network.elements
        nr, nt, _ = elements.shape

        for z in z_idx_clean:
            elements[:, :, z] = np.roll(elements[:, :, z], shift=n_step, axis=1)
            
            for r in range(nr):
                for t in range(nt):
                    el = elements[r, t, z]
                    if el is not None:
                        el.position = (r, t, z)
                        el.update_flat_position()
                        el.neighbor_elements_position = get_neighbor_elements_position(element=el).neighbor_elements_position

    else:
        reluctance_network.vectorized_elements.rotate_vectorized_elements(z_indices = z_indices,
                                                                          n_step = n_step)

        