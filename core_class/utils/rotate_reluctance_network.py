import numpy as np

def rotate_reluctance_network(reluctance_network, z_indices=(0, 1, 2), n_step=1):
    z_idx_clean = np.atleast_1d(z_indices).astype(int)
    elements = reluctance_network.elements
    
    for z in z_idx_clean:
        elements[:, :, z] = np.roll(elements[:, :, z], shift=n_step, axis=1)
        