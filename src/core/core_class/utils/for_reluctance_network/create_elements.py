from src.core.core_class.models.Element import Element
import numpy as np 

def create_elements(reluctance_network, debug=True, callback=None):

    nr = int(reluctance_network.mesh.n_cells_r)
    nt = int(reluctance_network.mesh.n_cells_t)
    nz = int(reluctance_network.mesh.n_cells_z)
    total_elements = nr * nt * nz
    
    elements = np.empty((nr, nt, nz), dtype=object, order='F')
    reluctance_network.elements = elements

    if debug is True:
        print("\033[94m\033[0m")
        print(f"\033[94mIn function create_elements.\033[0m")
        print("\033[94m{\033[0m")
        print(f"\033[94m    Total elements to create: {total_elements}\033[0m")

    for i_z in range(nz):
        for i_t in range(nt):
            for i_r in range(nr):
                position = (i_r, i_t, i_z)
                
                elements[i_r, i_t, i_z] = Element(
                    position=position,
                    reluctance_network=reluctance_network)
                
                current_index = i_z * (nt * nr) + i_t * nr + i_r + 1
                
                if current_index % 50 == 0 or current_index == total_elements:
                    percent = (current_index / total_elements) * 100
                    if debug is True:
                        print(f"\r\033[94m    Creating Elements: {percent:.1f}%\033[0m", end="", flush=True)
                    else:
                        print(f"\rCreating Elements: {percent:.1f}%", end="", flush=True)
                
                if callback:
                    if current_index % 50 == 0 or current_index == total_elements:
                        progress_val = int((current_index / total_elements) * 100)
                        callback(f"Creating elements: {current_index}/{total_elements}", progress_val)
                    
    print()

    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
    
    if debug is True:
        print("\033[94mIn function create_elements: Elements creation and network update completed.\033[0m")
        print("\033[94m}\033[0m")
        print("\033[94m\033[0m")

    return elements