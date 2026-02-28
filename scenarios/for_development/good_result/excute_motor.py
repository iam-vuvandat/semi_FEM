import paths
import numpy as np
import matplotlib.pyplot as plt
import math

from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
from src.core.storage.core import motor_io

RE_CREATE_MOTOR = False
RE_SOLVE        = False
SHOW_RELUCTANCE = True
FILENAME        = "AFT_Motor_Optimization"

if RE_CREATE_MOTOR:
    aft = AxialFluxMotorType1()

    stator = aft.geometry_data.stator
    stator.slot_number    = 18
    stator.stator_lam_dia = 160 * 1e-3
    stator.stator_bore_dia= 60 * 1e-3
    stator.slot_width     = 6.5 * 1e-3
    stator.slot_depth     = 18 * 1e-3
    stator.stator_length  = 30 * 1e-3

    rotor = aft.geometry_data.rotor
    rotor.pole_number     = 12
    rotor.airgap          = 1.0 * 1e-3
    rotor.magnet_length   = 5.0 * 1e-3
    rotor.magnet_arc      = 135
    
    aft.winding_data.turns         = 25
    aft.winding_data.phase         = 3
    aft.winding_data.parallel_path = 1
    aft.winding_data.winding_layer = 2

    aft.mechanical.shaft_speed = 3600.0
    aft.drive.set_control(i_rms=15.0, phase_advanced=0.0)

    mesh = aft.adaptive_mesh_data
    mesh.n_theta    = 180
    mesh.n_z_airgap = 1
    mesh.n_z_magnet = 1
    mesh.n_r_2      = 1

    aft.reload()
    aft.init_winding()

    motor_io.save_motor(motor_obj=aft, filename=FILENAME)
else:
    aft = motor_io.load_motor(filename=FILENAME)

if RE_CREATE_MOTOR or RE_SOLVE:
    calc = aft.calculation_data
    calc.max_relative_residual = 0.005
    calc.max_iteration         = 80
    calc.material_relax        = 0.35
    
    p_pairs = aft.geometry_data.rotor.pole_number / 2
    calc.n_point           = 3
    
    calc.solve_cogging     = False
    calc.solve_only_1_step = False
    calc.debug             = True

    aft.create_reluctance_network()
    aft.reluctance_network.show_elements()

    aft.analysis_motor()
    
    motor_io.save_motor(motor_obj=aft, filename=FILENAME)

if hasattr(aft.record, 'flux_linkage') and len(aft.record.flux_linkage) > 0:
    flux = aft.record.flux_linkage
    emf  = aft.record.back_emf
    mst  = aft.record.mst_data 
    
    theta_flux = flux[-1, :]
    theta_mst  = mst[-1, :]
    
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    speed_display = aft.mechanical.shaft_speed
    fig.suptitle(f"ANALYSIS: {FILENAME}\nSpeed: {speed_display} RPM", fontsize=14, fontweight='bold')
    
    colors = ['#e74c3c', '#2ecc71', '#3498db']

    for j in range(int(aft.winding_data.phase)):
        axs[0, 0].plot(theta_flux, flux[j, :], color=colors[j % 3], label=f'Phase {chr(65+j)}')
    axs[0, 0].set_title("Flux Linkage (Wb)", fontweight='bold')
    axs[0, 0].grid(True, ls='--', alpha=0.6)
    axs[0, 0].legend(loc='upper right')

    for j in range(int(aft.winding_data.phase)):
        axs[0, 1].plot(theta_flux, emf[j, :], color=colors[j % 3], label=f'Phase {chr(65+j)}')
    axs[0, 1].set_title("Back-EMF (V)", fontweight='bold')
    axs[0, 1].grid(True, ls='--', alpha=0.6)

    torque_z = mst[3, :]
    avg_t = np.mean(torque_z)
    axs[1, 0].plot(theta_mst, torque_z, color='#8e44ad', lw=2)
    axs[1, 0].axhline(y=avg_t, color='black', ls=':', label=f'Avg: {avg_t:.2f} Nm')
    axs[1, 0].set_title("Torque (Maxwell Stress)", fontweight='bold')
    axs[1, 0].set_xlabel("Position (rad)")
    axs[1, 0].set_ylabel("Nm")
    axs[1, 0].grid(True, ls='--', alpha=0.6)
    axs[1, 0].legend()

    force_z = mst[2, :]
    axs[1, 1].plot(theta_mst, force_z, color='#f39c12', lw=2)
    axs[1, 1].set_title("Axial Force Fz (N)", fontweight='bold')
    axs[1, 1].set_xlabel("Position (rad)")
    axs[1, 1].set_ylabel("Newton")
    axs[1, 1].grid(True, ls='--', alpha=0.6)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if SHOW_RELUCTANCE:
    aft.display()