import numpy as np
from core_class.utils.find_flat_position import find_flat_position

def rotate_reluctance_network(reluctance_network, z_indices=(0, 1, 2), n_step=1):
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
                    el.flat_position = find_flat_position(element=el).flat_position