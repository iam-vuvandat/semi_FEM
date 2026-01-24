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
re_create_motor = False
re_solve        = True
plot            = False
show_reluctance = True
filename        = "motor_ngon_1"

# --- Motor Initialization ---
if not re_create_motor:
    # Load motor from storage
    aft = motor_io.load_motor(filename=filename)
    if re_solve:
        # Clear light elements list to force re-computation in solver
        aft.reluctance_network.list_elements_lite = None
else:
    # Initialize new motor with refactored nested Container structure
    aft = AxialFluxMotorType1()
    
    # Execute CAD and Mesh generation
    aft.create_geometry()
    aft.create_adaptive_mesh()
    
    # Initialize the Reluctance Network solver
    aft.create_reluctance_network()
    
    # Save the initialized object state
    motor_io.save_motor(motor_obj=aft, filename=filename)

# --- Simulation & Solver Loop ---
if re_solve:
    # Access n_theta through the new nested adaptive_mesh_data container
    nodes_tangential = aft.mesh.adaptive_mesh_data.nodes_tangential_theta
    n_theta_steps = nodes_tangential - 1 
    
    n_step_shift = 6
    # Calculate simulation steps based on tangential resolution
    n_step_solve = int(n_theta_steps // n_step_shift)
    
    # For quick testing, we can override to 1 step
    n_step_solve = 3 
    
    # Initialize linkage array: 3 phases + 1 row for position
    flux_linkage = np.zeros((4, n_step_solve))
    
    for i in tqdm(range(n_step_solve), desc="Solving & Rotating"):
        # Run the non-linear MBGRN solver
        aft.reluctance_network.solve(
            method                = "adaptive_broyden",
            max_iteration         = 100,
            max_relative_residual = 0.05,
            material_relax        = 0.2, 
            damping_factor        = 1.0,   
            debug                 = True
        )
        
        if n_step_solve != 1:
            # Rotate rotor based on shift steps
            aft.rotate_rotor(n_step=n_step_shift)
            
            # Retrieve flux linkage results
            data_out = aft.reluctance_network.get_flux_linkage().flux_linkage
            flux_linkage[:, i] = data_out.flatten()
            
            # Store results in the record container
            aft.record.flux_linkage = flux_linkage
            
            # Convert RPM to Rad/s for Back-EMF calculation
            shaft_speed_rad_s = aft.shaft_speed * (2 * pi / 60)
            
            # Compute Back-EMF using periodic derivative
            aft.record.back_emf_phase = periodic_derivative(data=flux_linkage).derivative * shaft_speed_rad_s
            
    # Final save of the solved motor state
    motor_io.save_motor(motor_obj=aft, filename=filename)

# --- Result Visualization ---
if plot:
    flux_linkage   = aft.record.flux_linkage
    back_emf_data  = aft.record.back_emf_phase
    
    theta_position = flux_linkage[-1, :]   # Last row is Rotor Position
    psi_phases     = flux_linkage[:-1, :]  # Rows 0-2 are Flux Linkages

    # Plot Flux Linkage
    fig, ax = plt.subplots(figsize=(10, 6))
    labels = ['Phase A', 'Phase B', 'Phase C']
    colors = ['red', 'green', 'blue']

    for j in range(psi_phases.shape[0]):
        ax.plot(theta_position, psi_phases[j, :], label=labels[j], color=colors[j], linewidth=1.5)

    ax.set_xlabel("Rotor Position (Degree)")
    ax.set_ylabel("Flux Linkage (Wb)")
    ax.set_title("Magnetic Flux Linkage vs. Rotor Position")
    ax.grid(True, which='both', alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.show()

    # Plot Back-EMF
    theta_emf    = back_emf_data[-1, :] # Last row is position in Rad
    bemf_phases  = back_emf_data[:-1, :] # Phase A, B, C

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    labels = ['Back-EMF Phase A', 'Back-EMF Phase B', 'Back-EMF Phase C']

    for j in range(bemf_phases.shape[0]):
        ax2.plot(theta_emf, bemf_phases[j, :], label=labels[j], color=colors[j], linewidth=1.5)

    ax2.set_xlabel("Rotor Position (Rad)")
    ax2.set_ylabel("Back-EMF (V)")
    ax2.set_title("Back-EMF Waveforms")
    ax2.grid(True, which='both', alpha=0.3)
    ax2.legend()
    plt.tight_layout()
    plt.show()

# --- 3. Final Model Check ---
if show_reluctance:
    # Display the final CAD and simulation status
    aft.geometry.show()
    aft.display()