import numpy as np

def update_vectorized_flux_density_average(vectorized_elements):
    flux = vectorized_elements.flux_direct
    area = vectorized_elements.section_area
    
    # Tach 3 huong In (0,1,2) va 3 huong Out (3,4,5)
    flux_in = flux[0:3, :]
    flux_out = flux[3:6, :]
    
    area_in = area[0:3, :]
    area_out = area[3:6, :]
    
    # Tinh 3 thanh phan Br, Bt, Bz (3 hang)
    # Dung tong flux / tong area tren cung mot truc
    b_components = (flux_in + flux_out) / (area_in + area_out)
    
    # Tinh do lon B_mag (1 hang)
    b_mag = np.sqrt(np.sum(b_components**2, axis=0))
    
    # Cap nhat mang 4 hang [Br, Bt, Bz, B_mag]
    vectorized_elements.flux_density_average = np.vstack([b_components, b_mag])