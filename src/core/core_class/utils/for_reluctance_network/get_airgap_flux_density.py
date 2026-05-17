import numpy as np


def get_airgap_flux_density(reluctance_network, path_sweep=[0, -1, 0]):

    reluctance_network.refresh_elements()

    elements = reluctance_network.elements
    n_r, n_t, n_z = elements.shape

    total_column = 1
    if path_sweep[0] == -1:
        total_column = n_r
    elif path_sweep[1] == -1:
        total_column = n_t
    elif path_sweep[2] == -1:
        total_column = n_z

    airgap_flux_density = np.zeros((5, total_column))

    for i in range(total_column):
        if path_sweep[0] == -1:
            element = elements[i, path_sweep[1], path_sweep[2]]
        elif path_sweep[1] == -1:
            element = elements[path_sweep[0], i, path_sweep[2]]
        elif path_sweep[2] == -1:
            element = elements[path_sweep[0], path_sweep[1], i]

        b_avg = element.flux_density_average
        airgap_flux_density[0, i] = b_avg[0]
        airgap_flux_density[1, i] = b_avg[1]
        airgap_flux_density[2, i] = b_avg[2]
        airgap_flux_density[3, i] = b_avg[3]
        airgap_flux_density[4, i] = i

    return airgap_flux_density