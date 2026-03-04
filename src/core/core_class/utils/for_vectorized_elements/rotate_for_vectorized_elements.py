import numpy as np 
from src.core.core_class.utils.for_vectorized_elements.find_neighbor_indices import find_neighbor_indices

def rotate_for_vectorized_elements(vectorized_elements,
                                   z_indices = [0,1,2],
                                   n_step = 1):
    nr, nt, nz = vectorized_elements.virtual_shape
    z_idx_clean = np.atleast_1d(z_indices).astype(int)

    attributes_to_rotate = [
        'material', 'magnet_source', 
        'element_winding_vector', 'winding_source', 'magnetic_source','winding_normal',
        'minimum_reluctance', 'reluctance',
        'relative_permeability', 'flux_direct', 'flux_density_direct', 
        'flux_density_average'
    ]

    for attr_name in attributes_to_rotate:
        attr_data = getattr(vectorized_elements, attr_name)
        
        if attr_data.ndim == 1:
            # Tu 1D -> 3D (nr, nt, nz)
            reshaped = attr_data.reshape((nr, nt, nz), order='F')
            for z in z_idx_clean:
                reshaped[:, :, z] = np.roll(reshaped[:, :, z], shift=n_step, axis=1)
            setattr(vectorized_elements, attr_name, reshaped.ravel(order='F'))
        else:
            # Tu 2D -> 4D (dim, nr, nt, nz)
            dim = attr_data.shape[0]
            reshaped = attr_data.reshape((dim, nr, nt, nz), order='F')
            
            for z in z_idx_clean:
                # Xoay tren truc nt (Axis 2)
                reshaped[:, :, :, z] = np.roll(reshaped[:, :, :, z], shift=n_step, axis=2)
            
            # Ep tu 4D tro lai 2D (dim, total_elements)
            setattr(vectorized_elements, attr_name, reshaped.reshape((dim, -1), order='F'))

    # Bat buoc phai cap nhat lai neighbor indices
    vectorized_elements.neighbor_indices, vectorized_elements.neighbor_valid = find_neighbor_indices(vectorized_elements=vectorized_elements)