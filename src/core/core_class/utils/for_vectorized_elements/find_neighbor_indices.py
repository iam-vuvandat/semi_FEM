import numpy as np 

def find_neighbor_indices(vectorized_elements):
    nr, nt, nz = vectorized_elements.virtual_shape
    total_elements = nr * nt * nz
    indices = np.arange(total_elements)
    
    r, t, z = np.unravel_index(indices, (nr, nt, nz), order='F')
    
    neighbor_element = np.full((6, total_elements), -1, dtype=int)
    
    # Thứ tự: r-1, t-1, z-1, r+1, t+1, z+1
    offsets = [
        (-1, 0, 0), (0, -1, 0), (0, 0, -1), 
        (1, 0, 0), (0, 1, 0), (0, 0, 1)
    ]
    
    # SỬA TẠI ĐÂY: Đảm bảo periodic luôn có 3 phần tử [r, t, z]
    periodic = vectorized_elements.periodic_boundary 
    if isinstance(periodic, (bool, np.bool_)):
        # Nếu truyền vào True/False đơn lẻ, mặc định chỉ trục t (index 1) là chu kỳ
        periodic = [False, periodic, False]
    
    for row, (dr, dt, dz) in enumerate(offsets):
        nr_i, nt_i, nz_i = r + dr, t + dt, z + dz
        
        if dr != 0:
            if periodic[0]: nr_i %= nr
            mask_valid = (nr_i >= 0) & (nr_i < nr)
        elif dt != 0:
            if periodic[1]: nt_i %= nt
            mask_valid = (nt_i >= 0) & (nt_i < nt)
        else: # dz != 0
            if periodic[2]: nz_i %= nz
            mask_valid = (nz_i >= 0) & (nz_i < nz)
            
        if np.any(mask_valid):
            neighbor_element[row, mask_valid] = np.ravel_multi_index(
                (nr_i[mask_valid], nt_i[mask_valid], nz_i[mask_valid]), 
                (nr, nt, nz), 
                order='F'
            )
            
    neighbor_mask = (neighbor_element != -1).astype(int)
            
    return neighbor_element, neighbor_mask