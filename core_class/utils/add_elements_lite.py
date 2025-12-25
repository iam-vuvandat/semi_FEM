from core_class.models.ElementLite import ElementLite
import numpy as np 
from tqdm import tqdm

def add_elements_lite(reluctance_network):

    if reluctance_network.list_elements_lite is None:
        reluctance_network.list_elements_lite = []
    else:
        pass

    elements = reluctance_network.elements
    nr, nt, nz = elements.shape
    
    current_order = 'F' if np.isfortran(elements) else 'C'
    elements_lite = np.empty(elements.shape, dtype=object, order=current_order)

    total_elements = nr * nt * nz
    with tqdm(total=total_elements, desc="Creating ElementLite History") as pbar:
        for z in range(nz):
            for t in range(nt):
                for r in range(nr):
                    elements_lite[r, t, z] = ElementLite(elements[r, t, z])
                    pbar.update(1)

    reluctance_network.list_elements_lite.append(elements_lite)