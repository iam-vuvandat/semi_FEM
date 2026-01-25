import paths
import time
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io
from src.core.solver.utils.periodic_derivative import periodic_derivative
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import math

pi = math.pi

# --- Configuration ---
re_create_motor = False # Khuyến nghị True sau khi refactor để đồng bộ cấu trúc mới
re_solve        = False
plot            = False
show_reluctance = True
filename        = "motor_ngon_1"

# --- 1. MOTOR INITIALIZATION ---
if not re_create_motor:
    # Load motor from storage
    aft = motor_io.load_motor(filename=filename)
    if re_solve:
        # Xóa list_elements_lite để ép bộ giải tính toán lại trên lưới mới
        aft.reluctance_network.list_elements_lite = None
else:
    # Khởi tạo motor mới với cấu trúc đóng gói nguyên bản
    aft = AxialFluxMotorType1()
    
    # Lưu ý: Hàm reload() đã được gọi tự động trong __init__ của lớp motor 
    # để thực hiện create_geometry() và create_adaptive_mesh()
    
    # Khởi tạo Reluctance Network solver
    aft.create_reluctance_network()
    
    
    # Lưu trạng thái ban đầu
    motor_io.save_motor(motor_obj=aft, filename=filename)

aft.reluctance_network.display()

# --- 2. SIMULATION & SOLVER LOOP ---
if re_solve:
    # Truy cập n_theta qua tên gốc từ adaptive_mesh_data
    n_theta = aft.adaptive_mesh_data.n_theta
    n_theta_steps = n_theta - 1 
    
    n_step_shift = 6
    # Tính toán số bước giải dựa trên độ phân giải lưới
    n_step_solve = int(n_theta_steps // n_step_shift)
    
    # Override để test nhanh trên Surface Pro 5
    n_step_solve = 3 
    
    # Lấy số pha từ cấu trúc winding_data
    phase_number = aft.winding_data.phase
    
    # Khởi tạo mảng từ thông: (số pha + 1 dòng vị trí) x số bước
    flux_linkage = np.zeros((phase_number + 1, n_step_solve))
    
    for i in tqdm(range(n_step_solve), desc="Solving & Rotating"):
        # Chạy bộ giải phi tuyến MBGRN
        aft.reluctance_network.solve(
            method                = "adaptive_broyden",
            max_iteration         = 100,
            max_relative_residual = 0.05,
            material_relax        = 0.2, 
            damping_factor        = 1.0,   
            debug                 = True
        )
        
        # Lấy kết quả từ thông liên kết từ phương thức đã refactor
        # Kết quả trả về đối tượng Output chứa flux_linkage_results
        data_out = aft.reluctance_network.get_flux_linkage().flux_linkage
        flux_linkage[:, i] = data_out.flatten()
        
        if n_step_solve != 1:
            # Xoay rotor dựa trên bước dịch lưới
            aft.rotate_rotor(n_step=n_step_shift)
            
    # Lưu kết quả vào record container
    aft.record.flux_linkage = flux_linkage
    
    # Tính toán Back-EMF
    # Đổi RPM sang Rad/s: $\omega = n \cdot \frac{2\pi}{60}$
    shaft_speed_rad_s = aft.shaft_speed * (2 * pi / 60)
    
    # Đạo hàm từ thông theo thời gian: $e = \frac{d\Psi}{dt} = \frac{d\Psi}{d\theta} \cdot \omega$
    aft.record.back_emf_phase = periodic_derivative(data=flux_linkage).derivative * shaft_speed_rad_s
            
    # Lưu trạng thái motor sau khi giải
    motor_io.save_motor(motor_obj=aft, filename=filename)

# --- 3. RESULT VISUALIZATION ---
if plot:
    flux_linkage   = aft.record.flux_linkage
    back_emf_data  = aft.record.back_emf_phase
    
    theta_position = flux_linkage[-1, :]   # Dòng cuối là vị trí Rotor
    psi_phases     = flux_linkage[:-1, :]  # Các dòng đầu là Flux Linkages
    
    colors = ['red', 'green', 'blue', 'orange', 'purple', 'black']

    # Biểu đồ Flux Linkage
    fig, ax = plt.subplots(figsize=(10, 6))
    for j in range(psi_phases.shape[0]):
        ax.plot(theta_position, psi_phases[j, :], 
                label=f'Phase {chr(65+j)}', color=colors[j % len(colors)], linewidth=1.5)

    ax.set_xlabel("Rotor Position (Rad)")
    ax.set_ylabel("Flux Linkage (Wb)")
    ax.set_title("Magnetic Flux Linkage vs. Rotor Position")
    ax.grid(True, which='both', alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.show()

    # Biểu đồ Back-EMF
    theta_emf   = back_emf_data[-1, :] 
    bemf_phases = back_emf_data[:-1, :] 

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    for j in range(bemf_phases.shape[0]):
        ax2.plot(theta_emf, bemf_phases[j, :], 
                 label=f'Back-EMF Phase {chr(65+j)}', color=colors[j % len(colors)], linewidth=1.5)

    ax2.set_xlabel("Rotor Position (Rad)")
    ax2.set_ylabel("Back-EMF (V)")
    ax2.set_title("Back-EMF Waveforms")
    ax2.grid(True, which='both', alpha=0.3)
    ax2.legend()
    plt.tight_layout()
    plt.show()

# --- 4. FINAL MODEL CHECK ---
if show_reluctance:
    # Hiển thị Geometry và thông tin motor
    
    aft.display()