import paths
import numpy as np
import matplotlib.pyplot as plt
import math

# Import các thành phần hệ thống
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io

# Thiết lập các tham số điều khiển
RE_CREATE_MOTOR = True  # True: Tạo mới động cơ | False: Nạp từ file
RE_SOLVE        = True   # True: Chạy lại Solver | False: Chỉ vẽ dữ liệu cũ
SHOW_RELUCTANCE = True  # Hiển thị cấu trúc mạng từ trở
FILENAME        = "motor_ngon_2"

# 1. Quản lý đối tượng Motor
if RE_CREATE_MOTOR:
    print(f">>> Đang tạo mới động cơ...")
    aft = AxialFluxMotorType1()

    aft.adaptive_mesh_data.n_r_in          = 1
    aft.adaptive_mesh_data.n_r_1           = 1
    aft.adaptive_mesh_data.n_r_2           = 2
    aft.adaptive_mesh_data.n_r_3           = 2
    aft.adaptive_mesh_data.n_r_out         = 1
    aft.adaptive_mesh_data.n_theta         = 70
    aft.adaptive_mesh_data.n_z_in_air      = 1
    aft.adaptive_mesh_data.n_z_rotor_yoke  = 1
    aft.adaptive_mesh_data.n_z_magnet      = 1
    aft.adaptive_mesh_data.n_z_airgap      = 1
    aft.adaptive_mesh_data.n_z_tooth_tip_1 = 1
    aft.adaptive_mesh_data.n_z_tooth_tip_2 = 2
    aft.adaptive_mesh_data.n_z_tooth_body  = 3
    aft.adaptive_mesh_data.n_z_stator_yoke = 1
    aft.adaptive_mesh_data.n_z_out_air     = 1

    aft.winding_data.turns = 15

    aft.reload()

    # Lưu lần đầu để tạo cấu trúc file
    motor_io.save_motor(motor_obj=aft, filename=FILENAME)
else:
    print(f">>> Đang nạp động cơ từ file: {FILENAME}")
    aft = motor_io.load_motor(filename=FILENAME)

# 2. Thực hiện tính toán (Solver)
if RE_CREATE_MOTOR or RE_SOLVE:
    print(">>> Khởi động quá trình phân tích (Analysis Motor)...")
    
    # Xóa cache lưới cũ nếu cần giải lại
    if aft.reluctance_network is not None:
        aft.reluctance_network.list_elements_lite = None
    
    # Gọi hàm giải chính
    aft.calculation_data.max_relative_residual = 0.05
    aft.calculation_data.max_iteration = 50
    aft.calculation_data.material_relax = 0.35
    aft.calculation_data.solve_cogging = True
    aft.calculation_data.n_point = 18
    aft.calculation_data.debug = True

    aft.analysis_motor()
    
    # Lưu kết quả sau khi giải
    motor_io.save_motor(motor_obj=aft, filename=FILENAME)
    print(">>> Đã lưu kết quả phân tích.")

# 3. Trực quan hóa kết quả (Plotting)
if hasattr(aft.record, 'flux_linkage'):
    print(">>> Đang vẽ đồ thị kết quả...")
    
    # Trích xuất dữ liệu từ Record
    flux = aft.record.flux_linkage
    emf  = aft.record.back_emf
    mst  = aft.record.mst_data  # Dữ liệu này đã được duplicate_data (2 chu kỳ)
    
    # Trục góc (Radian)
    theta_flux = flux[-1, :]
    theta_mst  = mst[-1, :]
    
    # Cấu hình Figure
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"Kết quả mô phỏng: {FILENAME} ({aft.shaft_speed} RPM)", fontsize=16, fontweight='bold')
    colors = ['#d62728', '#2ca02c', '#1f77b4'] # Đỏ, Lục, Lam đại diện 3 pha

    # Biểu đồ 1: Từ thông liên kết (Flux Linkage)
    for j in range(aft.winding_data.phase):
        axs[0, 0].plot(theta_flux, flux[j, :], color=colors[j % 3], 
                       label=f'Pha {chr(65+j)}', linewidth=1.5)
    axs[0, 0].set_title("Từ thông liên kết (Flux Linkage)", fontweight='bold')
    axs[0, 0].set_ylabel("Flux (Wb)")
    axs[0, 0].grid(True, alpha=0.3)
    axs[0, 0].legend()

    # Biểu đồ 2: Sức điện động (Back-EMF)
    for j in range(aft.winding_data.phase):
        axs[0, 1].plot(theta_flux, emf[j, :], color=colors[j % 3], 
                       label=f'Pha {chr(65+j)}', linewidth=1.5)
    axs[0, 1].set_title("Sức điện động (Back-EMF Terminal)", fontweight='bold')
    axs[0, 1].set_ylabel("Voltage (V)")
    axs[0, 1].grid(True, alpha=0.3)

    # Biểu đồ 3: Mô-men xoắn (Torque) - 2 chu kỳ
    torque_z = mst[3, :]
    avg_torque = np.mean(torque_z)
    axs[1, 0].plot(theta_mst, torque_z, color='purple', label='Torque')
    axs[1, 0].axhline(y=avg_torque, color='black', linestyle='--', alpha=0.7, 
                      label=f'Avg: {avg_torque:.2f} Nm')
    axs[1, 0].set_title("Mô-men điện từ (Maxwell Stress)", fontweight='bold')
    axs[1, 0].set_ylabel("Torque (Nm)")
    axs[1, 0].set_xlabel("Vị trí Rotor (rad)")
    axs[1, 0].grid(True, alpha=0.3)
    axs[1, 0].legend()

    # Biểu đồ 4: Lực dọc trục (Axial Force) - 2 chu kỳ
    force_z = mst[2, :]
    axs[1, 1].plot(theta_mst, force_z, color='darkorange', label='Axial Force')
    axs[1, 1].set_title("Lực dọc trục (Fz)", fontweight='bold')
    axs[1, 1].set_ylabel("Force (N)")
    axs[1, 1].set_xlabel("Vị trí Rotor (rad)")
    axs[1, 1].grid(True, alpha=0.3)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

# Hiển thị cấu trúc mạng nếu bật
if SHOW_RELUCTANCE:
    aft.display()