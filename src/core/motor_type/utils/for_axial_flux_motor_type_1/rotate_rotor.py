import numpy as np

def rotate_rotor(motor, n_step):
    """
    Rotates the rotor layers within the Reluctance Network by a specified number of steps.
    Restored original variable names: n_z_in_air, n_z_rotor_yoke, n_z_magnet.
    """
    # 1. Truy cập container adaptive_mesh_data từ đối tượng mesh của motor
    # Dữ liệu này đã được đóng gói trong quá trình refactor AxialFluxMotorType1
    mesh_data = motor.mesh.adaptive_mesh_data
    
    # 2. Trích xuất các tham số chia lưới theo tên gốc
    n_z_in_air      = mesh_data.n_z_in_air
    n_z_rotor_yoke  = mesh_data.n_z_rotor_yoke
    n_z_magnet      = mesh_data.n_z_magnet

    # 3. Tính toán số lượng lớp (layers) theo phương trục Z cần được xoay
    
    number_of_layers_to_rotate = (n_z_in_air + 
                                  n_z_rotor_yoke + 
                                  n_z_magnet )
    
    # 4. Tạo dải chỉ số Z thuộc về cụm Rotor
    z_indices_to_rotate = np.arange(number_of_layers_to_rotate)
    
    # 5. Thực thi việc xoay trong lõi bộ giải Reluctance Network
    reluctance_network = motor.reluctance_network
    
    if reluctance_network is not None:
        reluctance_network.rotate(z_indices = z_indices_to_rotate,
                                  n_step    = n_step)
    else:
        print("[WARNING] Reluctance Network is not initialized. Cannot rotate.")