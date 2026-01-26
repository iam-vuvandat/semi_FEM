import paths
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import math

pi = math.pi

re_create_motor = True
re_solve        = True
plot            = True
show_reluctance = True
filename        = "motor_ngon_1"


if not re_create_motor:
    aft = motor_io.load_motor(filename=filename)
    if re_solve:
        aft.reluctance_network.list_elements_lite = None
else:
    aft = AxialFluxMotorType1()
    motor_io.save_motor(motor_obj=aft, filename=filename)
    aft.analysis_motor(max_relative_residual = 0.03,
                        max_iteration=50,
                        material_relax=0.4,
                        solve_cogging = False,
                        n_point = 30,
                        debug = True)

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

if show_reluctance:    
    aft.display()