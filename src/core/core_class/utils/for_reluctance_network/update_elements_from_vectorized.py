import numpy as np
import time

def update_elements_from_vectorized(reluctance_network):
    if reluctance_network.vectorized_optimization is True:
        start_time = time.perf_counter()
        vectorized_elements = reluctance_network.vectorized_elements
        elements_flat = reluctance_network.elements.ravel(order='F')
        
        # Anh xa tu so sang chuoi cho material
        material_map = {0: "air", 1: "magnet", 2: "iron"}
        
        for i, element in enumerate(elements_flat):
            # 1. Cap nhat cac bien trang thai (State variables)
            
            element.reluctance = vectorized_elements.reluctance[:, i].reshape((2, 3))
            element.relative_permeability = vectorized_elements.relative_permeability[:, i].reshape((2, 3))
            element.flux_direct = vectorized_elements.flux_direct[:, i].reshape((2, 3))
            element.flux_density_direct = vectorized_elements.flux_density_direct[:, i].reshape((2, 3))
            element.flux_density_average = vectorized_elements.flux_density_average[:, i]
            
            
            # Anh xa material tu so ve chuoi
            mat_value = int(vectorized_elements.material[i])
            element.material = material_map.get(mat_value, "air")
            
            
            element.magnet_source = vectorized_elements.magnet_source[:, i].reshape((2, 3))
            element.winding_source = vectorized_elements.winding_source[:, i].reshape((2, 3))
            element.magnetic_source = vectorized_elements.magnetic_source[:, i].reshape((2, 3))
            element.element_winding_vector = vectorized_elements.element_winding_vector[:, i]
            element.winding_normal = vectorized_elements.winding_normal[:, i]

        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"Thời gian cập nhật element: {duration}")
        