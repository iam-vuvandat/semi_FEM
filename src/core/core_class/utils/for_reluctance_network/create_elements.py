from src.core.core_class.models.Element import Element
import numpy as np 
from tqdm import tqdm

def create_elements(reluctance_network, debug=True, callback=None):

    nr = int(reluctance_network.mesh.n_cells_r)
    nt = int(reluctance_network.mesh.n_cells_t)
    nz = int(reluctance_network.mesh.n_cells_z)
    total_elements = nr * nt * nz
    
    elements = np.empty((nr, nt, nz), dtype=object, order='F')
    reluctance_network.elements = elements

    with tqdm(total=total_elements, desc="Creating Elements", disable=not debug) as pbar:
        for i_z in range(nz):
            for i_t in range(nt):
                for i_r in range(nr):
                    position = (i_r, i_t, i_z)
                    
                    elements[i_r, i_t, i_z] = Element(
                        position=position,
                        reluctance_network=reluctance_network)
                    
                    pbar.update(1)
                    
                    # Phát tín hiệu về UI thông qua callback
                    if callback:
                        # Tính toán chỉ số hiện tại dựa trên 3 vòng lặp
                        current_index = i_z * (nt * nr) + i_t * nr + i_r + 1
                        # Gửi phần trăm về ProgressBar mỗi khi xong một rãnh/phần tử
                        if current_index % 10 == 0 or current_index == total_elements:
                            progress_val = int((current_index / total_elements) * 100)
                            callback(progress_val)
                    
    reluctance_network.update_reluctance_network(magnetic_potential=reluctance_network.magnetic_potential)
    return elements