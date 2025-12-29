import paths
from system.core import libraries_require
from motor_type.models.AxialFluxMotorType1 import AxialFluxMotorType1
from storage.core import workspace 
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt

re_create_motor = True
re_solve = True

if not re_create_motor:
    aft = workspace.load("aft1")
    if re_solve:
        aft.reluctance_network.list_elements_lite = None
else:
    aft = AxialFluxMotorType1(magnet_length=5.0 * 1e-3, airgap=0.4 * 1e-3)
    aft.create_geometry()
    aft.create_adaptive_mesh()
    aft.create_reluctance_network()
    aft.reluctance_network.update_reluctance_network(magnetic_potential=aft.reluctance_network.magnetic_potential)
    workspace.save(aft1=aft)

if re_solve:
    n_theta = aft.mesh.detail_parameter[5] - 1 
    n_step_shift = 5
    n_step_solve = int(n_theta // n_step_shift)

    flux_linkage = np.zeros((4, n_step_solve))

    for i in tqdm(range(n_step_solve), desc="Solving & Rotating"):
        aft.reluctance_network.solve_magnetic_equation()
        aft.rotate_rotor(n_step=n_step_shift)
        
        data_out = aft.reluctance_network.get_flux_linkage().flux_linkage
        flux_linkage[:, i] = data_out.flatten()

    workspace.save(aft1=aft)

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

aft.reluctance_network.show()