import paths 
import numpy as np
import math 
from tqdm import tqdm
pi = math.pi
from src.core.solver.utils.periodic_derivative import periodic_derivative
from src.core.solver.utils.duplicate_data import duplicate_data

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
    minimum_theta_cell = int(math.ceil((symmetry_angle / delta_theta) - epsilon))

    # kiểm tra xem động cơ có lưới chưa
    if motor.mesh is None:
        motor.reload()
        motor.mesh.adaptive_mesh_data.n_theta = minimum_theta_cell 
        motor.reload()
        motor.create_reluctance_network()
    else:
        if int(motor.mesh.adaptive_mesh_data.n_theta) == minimum_theta_cell :
            pass
        else:
            motor.reload()
            motor.mesh.adaptive_mesh_data.n_theta = minimum_theta_cell 
            motor.reload()
            motor.create_reluctance_network()

    # Trích xuất số pha
    phase_number = motor.winding_data.phase

    # khởi tạo các mảng rỗng để lưu thông tin (các hàng đầu là dữ liệu từng pha, hàng cuối là vị trí góc (theta))
    
    flux_linkage = np.zeros((phase_number + 1,n_point))
    back_emf = np.zeros((phase_number + 1,n_point))
    mst_data = np.zeros((5,n_point))
    
    # bước xoay cell cogging: 
    n_step_cogging = 1 
    
    # bước xoay tiêu chuẩn: 
    n_step_standard = angle_factor

    # theo dõi số bước đã xoay 
    cogging_shifted = 0


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
                mst_data[:,i] = motor.maxwell_stress_tensor().mst_result

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


    motor.record.flux_linkage = flux_linkage.copy()
    # Xác định back emf
    # Tốc độ quay của trục (đổi sang rad/s)
    shaft_speed = motor.shaft_speed * (pi/30)

    
    back_emf = periodic_derivative(data=flux_linkage,half_open_interval= True).derivative * shaft_speed 
    if motor.mesh.adaptive_mesh_data.use_symmetry_factor is True:
        back_emf = back_emf * motor.symmetry_factor

    motor.record.back_emf = back_emf.copy()

    mst_data = duplicate_data(data=mst_data,half_open_interval = True).duplicated_data
    motor.record.mst_data = mst_data.copy()

    return None





