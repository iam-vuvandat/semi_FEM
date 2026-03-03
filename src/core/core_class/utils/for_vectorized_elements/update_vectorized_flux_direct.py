import numpy as np

def update_vectorized_flux_direct(vectorized_elements):
    phi = vectorized_elements.magnetic_potential
    indices = vectorized_elements.neighbor_indices
    mask = vectorized_elements.neighbor_valid
    reluctance = vectorized_elements.reluctance
    source = vectorized_elements.magnetic_source

    opp = [3, 4, 5, 0, 1, 2]
    flux_direct = np.zeros_like(reluctance)

    for k in range(6):
        m_k = mask[k]
        idx_k = indices[k]
        
        phi_neighbor = np.take(phi, idx_k, mode='clip')
        r_neighbor = np.take(reluctance[opp[k]], idx_k, mode='clip')
        f_neighbor = np.take(source[opp[k]], idx_k, mode='clip')

        if k < 3:
            begin_p, end_p = phi_neighbor, phi
        else:
            begin_p, end_p = phi, phi_neighbor

        numerator = (begin_p - end_p) + (source[k] + f_neighbor)
        denominator = reluctance[k] + r_neighbor

        flux_direct[k] = np.where(m_k == 1, numerator / denominator, 0.0)

    # Day ket qua vao property cua doi tuong
    vectorized_elements.flux_direct = flux_direct