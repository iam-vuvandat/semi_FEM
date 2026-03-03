import numpy as np

def update_permeability(vectorized_elements, material_relaxation_factor=1.0, delta_mu_max=-1):
    MU0 = 4 * np.pi * 1e-7
    
    # Lay du lieu dau vao
    material_mask = vectorized_elements.material
    B = vectorized_elements.flux_density_direct
    mu_old = vectorized_elements.relative_permeability
    
    database = vectorized_elements.reluctance_network.material_database
    
    # Khoi tao mang ket qua mu_next
    mu_next = np.empty_like(B)
    
    # 1. Xu ly vung khong phai sat (Tuyen tinh)
    air_mask = (material_mask == 0)
    magnet_mask = (material_mask == 1)
    
    mu_next[:, air_mask] = database.air.relative_permeance
    mu_next[:, magnet_mask] = database.magnet.relative_permeance
    
    # 2. Xu ly vung sat (Phi tuyen) - Toi uu bang cach chi tinh tren index sat
    iron_indices = np.where(material_mask == 2)[0]
    
    if iron_indices.size > 0:
        B_iron = B[:, iron_indices]
        B_abs = np.abs(B_iron)
        
        # Lay bang du lieu B-H
        B_table = np.asarray(database.iron.B_H_curve["B_data"])
        H_table = np.asarray(database.iron.B_H_curve["H_data"])
        
        # Noi suy H tu B_abs
        H_iron = np.interp(B_abs, B_table, H_table)
        
        # Tinh mu_iron (Xu ly diem ky di tai B=0)
        # Lay mu_initial tai diem dau tien cua bang neu B gan bang 0
        mu_at_zero = (B_table[1] / H_table[1]) / MU0 if H_table[1] != 0 else 2000.0
        
        mu_iron = np.where(
            B_abs < 1e-9, 
            mu_at_zero, 
            B_abs / (MU0 * H_iron + 1e-15)
        )
        
        # Ap dung relaxation va clipping chi cho vung sat
        mu_relaxed = (1 - material_relaxation_factor) * mu_old[:, iron_indices] + \
                     material_relaxation_factor * mu_iron
        
        if delta_mu_max != -1:
            mu_final_iron = np.clip(
                mu_relaxed, 
                a_min=mu_old[:, iron_indices] - delta_mu_max, 
                a_max=mu_old[:, iron_indices] + delta_mu_max
            )
        else:
            mu_final_iron = mu_relaxed
            
        mu_next[:, iron_indices] = mu_final_iron

    # Cap nhat ket qua cuoi cung (Dam bao mu >= 1)
    vectorized_elements.relative_permeability = np.maximum(mu_next, 1.0)