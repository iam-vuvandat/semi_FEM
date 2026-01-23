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

re_create_motor = False
re_solve = False
plot = False
show_reluctance = True
filename = "motor_ngon_1"

if not re_create_motor:
    aft = motor_io.load_motor(filename= filename)
    if re_solve:
        aft.reluctance_network.list_elements_lite = None
else:
    aft = AxialFluxMotorType1(magnet_length= 3.0 * 1e-3,
                              airgap=1.0 * 1e-3,
                              stator_length = 25* 1e-3,
                              rotor_length = 10 * 1e-3)
    
    aft.create_geometry()

    aft.create_adaptive_mesh(n_r_in              =2,
                         n_r_1                   =3,
                         n_r_2                   =7,
                         n_r_3                   =3,
                         n_r_out                 =2,
                         n_theta                 =120,
                         n_z_in_air              =2,
                         n_z_rotor_yoke          =4,
                         n_z_magnet              =2,
                         n_z_airgap              =4,
                         n_z_tooth_tip_1         =2,
                         n_z_tooth_tip_2         =3,
                         n_z_tooth_body          =5,
                         n_z_stator_yoke         =4,
                         n_z_out_air             =2, 
                         use_symmetry_factor=True,
                         periodic_boundary=True)
    
    aft.create_reluctance_network()
    motor_io.save_motor(motor_obj=aft,filename=filename)

if re_solve:
    n_theta = aft.mesh.detail_parameter[5] - 1 
    n_step_shift =6
    n_step_solve = int(n_theta // n_step_shift)
    n_step_solve = 1
    flux_linkage = np.zeros((4, n_step_solve))
    
    for i in tqdm(range(n_step_solve), desc="Solving & Rotating"):
        aft.reluctance_network.solve(method = "adaptive_broyden",
              max_iteration=100,
              max_relative_residual = 0.05,
              material_relax=0.2, 
              damping_factor = 1.0,   
              debug = True)
        
        if n_step_solve != 1:
            aft.rotate_rotor(n_step=n_step_shift)
            data_out = aft.reluctance_network.get_flux_linkage().flux_linkage
            flux_linkage[:, i] = data_out.flatten()
            aft.record.flux_linkage = flux_linkage
            shaft_speed = aft.shaft_speed #rpm
            shaft_speed *= 2*pi / 60 # rad/s
            aft.record.back_emf_phase = periodic_derivative(data=flux_linkage).derivative * shaft_speed
            
    motor_io.save_motor(motor_obj=aft,filename=filename)

if plot:
    flux_linkage=aft.record.flux_linkage
    back_emf_data = aft.record.back_emf_phase
    theta = flux_linkage[-1, :]
    psi_data = flux_linkage[:-1, :]

    fig, ax = plt.subplots(figsize=(10, 6))
    labels = ['Phase A', 'Phase B', 'Phase C']
    colors = ['red', 'green', 'blue']

    for j in range(psi_data.shape[0]):
        ax.plot(theta, psi_data[j, :], label=labels[j], color=colors[j], linewidth=1.5)

    ax.set_xlabel("Rotor Position (Degree)")
    ax.set_ylabel("Flux Linkage (Wb)")
    ax.set_title("Magnetic Flux Linkage vs. Rotor Position")
    ax.grid(True, which='both', alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.show()

    theta_emf = back_emf_data[-1, :]  # Hàng cuối là Theta
    bemf_phases = back_emf_data[:-1, :]  # Các hàng trên là Phase A, B, C

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    labels = ['Back-EMF Phase A', 'Back-EMF Phase B', 'Back-EMF Phase C']
    colors = ['red', 'green', 'blue']

    for j in range(bemf_phases.shape[0]):
        ax2.plot(theta_emf, bemf_phases[j, :], label=labels[j], color=colors[j], linewidth=1.5)

    ax2.set_xlabel("Rotor Position (Rad)")
    ax2.set_ylabel("Back-EMF (V)")
    ax2.set_title("Back-EMF Waveforms")
    ax2.grid(True, which='both', alpha=0.3)
    ax2.legend()
    plt.tight_layout()
    plt.show()

if show_reluctance:
    aft.geometry.show()
    aft.display()
    




