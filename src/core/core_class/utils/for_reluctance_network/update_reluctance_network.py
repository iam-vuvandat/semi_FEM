from tqdm import tqdm

def update_reluctance_network(reluctance_network, 
                              magnetic_potential=None,
                              winding_current=None,
                              update_for_magnetic_potential=False,
                              update_for_winding_current=False,
                              material_relaxation_factor=1.0,
                              delta_mu_max=-1,
                              debug=False):
    
    if update_for_magnetic_potential:
        reluctance_network.magnetic_potential = magnetic_potential
        
    if update_for_winding_current:
        reluctance_network.winding_current = winding_current

    # Kiểm tra xem có ĐỦ ĐIỀU KIỆN để chạy vectorized hay không
    use_vectorized = (reluctance_network.vectorized_optimization is True and 
                      reluctance_network.vectorized_elements is not None)

    if use_vectorized:
        # Luồng siêu tốc
        reluctance_network.vectorized_elements.update_vectorized_elements(
            magnetic_potential=magnetic_potential,
            winding_current=winding_current,
            update_for_magnetic_potential=update_for_magnetic_potential,
            update_for_winding_current=update_for_winding_current,
            material_relaxation_factor=material_relaxation_factor,
            delta_mu_max=delta_mu_max
        )
    else:
        # Luồng dự phòng (OOP): Chạy khi chưa init vectorized hoặc khi tắt tối ưu
        iterator = tqdm(reluctance_network.elements.flat, 
                        total=reluctance_network.elements.size, 
                        desc="Updating Network", 
                        disable=not debug)

        for element in iterator:
            if element is not None:
                element.update_element(
                    magnetic_potential=magnetic_potential,
                    winding_current=winding_current,
                    update_for_magnetic_potential=update_for_magnetic_potential,
                    update_for_winding_current=update_for_winding_current,
                    material_relaxation_factor=material_relaxation_factor,
                    delta_mu_max=delta_mu_max
                )