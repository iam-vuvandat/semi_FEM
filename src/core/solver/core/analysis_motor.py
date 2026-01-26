import paths 
import numpy as np
import math 
from tqdm import tqdm
pi = math.pi

def analysis_motor(motor,
                   max_relative_residual = 0.01,
                   max_iteration=50,
                   material_relax=0.4,
                   solve_cogging = True,
                   n_point = 30,
                   debug = True):
    
    # sai số máy
    epsilon = 1e-12

    # đọc dữ liệu: 
    # hệ số tuần hoàn
    symmetry_factor = motor.symmetry_factor
    symmetry_angle = 2*pi / symmetry_factor

    # chu kì cogging 
    cogging_angle = motor.cogging_period_mech

    # tỉ số giữa cogging_angle và symmetry_angle
    angle_factor = int(symmetry_angle // cogging_angle) # Hệ số này về bản chất luồn là số nguyên

    # để solve được n_point cogging: 
    delta_theta  = cogging_angle / (n_point)

    # số lượng cell hướng theta cần thiết: 
    minimum_theta_cell = math.ceil((symmetry_angle / delta_theta) - epsilon)

    # kiểm tra xem động cơ có lưới chưa
    if motor.mesh is None:
        motor.reload()
        motor.mesh.adaptive_mesh_data.n_theta = minimum_theta_cell + 1 # số lượng nút = số cell + 1
        motor.reload()
        motor.create_reluctance_network()
    else:
        if motor.mesh.adaptive_mesh_data.n_theta == minimum_theta_cell + 1 :
            pass
        else:
            motor.reload()
            motor.mesh.adaptive_mesh_data.n_theta = minimum_theta_cell + 1 # số lượng nút = số cell + 1
            motor.reload()
            motor.create_reluctance_network()

    # Trích xuất số pha
    phase_number = motor.winding_data.phase

    # khởi tạo các mảng rỗng để lưu thông tin (các hàng đầu là dữ liệu từng pha, hàng cuối là vị trí góc (theta))
    data_size = (phase_number + 1,n_point)
    flux_linkage = np.zeros(data_size)
    
    # bước xoay cell cogging: 
    n_step_cogging = 1 
    
    # bước xoay tiêu chuẩn: 
    n_step_standard = angle_factor

    # theo dõi số bước đã xoay 
    cogging_shifted = 0

    # Tham chiếu đến vị trí rotor: 
    current_position = motor.reluctance_network.current_position

    # quét số lượng cell theo hướng theta:
    for i in tqdm(range(minimum_theta_cell), desc=" Solving", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", ncols=70, ascii=False, colour="red", leave=False, disable=not debug):
        if solve_cogging:
            is_cogging_point = (i < n_point)
        else:
            is_cogging_point = False

        is_standard_point = (i % n_step_standard == 0)

        # --- Khung xử lý logic giải và trích xuất dữ liệu ---
        if is_cogging_point or is_standard_point:
            motor.reluctance_network.solve(method = "adaptive_broyden",
                                            load_step = 1,
                                            max_relative_residual =max_relative_residual ,
                                            max_iteration=  max_iteration,
                                            material_relax=material_relax, 
                                            damping_factor = 1.0,   
                                            debug = debug)
            
            if is_cogging_point:
                pass
            if is_standard_point:
                motor.reluctance_network.add_elements_lite()
                index_standard = i // n_step_standard
                if index_standard < n_point:
                    flux_linkage[:,index_standard] = motor.reluctance_network.get_flux_linkage().flux_linkage[:,0]
                cogging_shifted = 0

       
        if is_cogging_point:
            motor.rotate_rotor(n_step=n_step_cogging)
            cogging_shifted += n_step_cogging
        else:
            if is_standard_point:
                jump_step = int(n_step_standard - cogging_shifted)
                motor.rotate_rotor(n_step=jump_step)
                cogging_shifted = 0

    
    # xử lý symmetry:
    use_symmetry_factor = motor.mesh.adaptive_mesh_data.use_symmetry_factor
    if use_symmetry_factor: 
        symmetry_factor = motor.symmetry_factor
    else:
        symmetry_factor = 1.0

    flux_linkage = flux_linkage * symmetry_factor

    motor.record.flux_linkage = flux_linkage

    return None





