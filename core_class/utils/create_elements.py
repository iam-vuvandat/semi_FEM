from core_class.models.Element import Element
import numpy as np 
from tqdm import tqdm

def create_elements(motor, debug=True):
    nr = int(motor.mesh.n_cells_r)
    nt = int(motor.mesh.n_cells_t)
    nz = int(motor.mesh.n_cells_z)
    
    total_elements = nr * nt * nz
    
    elements = np.empty((nr, nt, nz), dtype=object, order='F')
    
    if debug:
        print(f"[INFO] Initializing {total_elements} elements...")

    with tqdm(total=total_elements, desc="Creating Elements", disable=not debug) as pbar:
        for i_z in range(nz):
            for i_t in range(nt):
                for i_r in range(nr):
                    position = (i_r, i_t, i_z)
                    
                    elements[i_r, i_t, i_z] = Element(
                        position=position,
                        motor=motor,
                        geometry=motor.geometry,
                        mesh=motor.mesh,
                        magnetic_potential=motor.magnetic_potential,
                        winding_current=motor.winding_current,
                        elements=elements
                    )
                    pbar.update(1)

    return elements