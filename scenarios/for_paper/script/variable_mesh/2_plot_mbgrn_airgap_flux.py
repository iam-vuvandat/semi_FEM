import paths
import matplotlib.pyplot as plt
from src.core.storage.core.MotorIO import MotorIO
from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style

io = MotorIO()
s = apply_journal_style()
fig_width, fig_height = 10, 10 / 1.5

number_of_configuation = 5
file_name_array = [f"motor_for_paper{i}" for i in range(number_of_configuation)]

plt.figure(figsize=(fig_width, fig_height))
for i in range(number_of_configuation):
    aft = io.load(path=file_name_array[i])
    aft.require('mesh')
    record = aft.record
    if hasattr(record, 'airgap_flux_density') and record.airgap_flux_density is not None:
        x_axis = record.airgap_flux_density[4, :]
        B_z = record.airgap_flux_density[2, :]
        total_cells = aft.mesh.total_cells
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            x_axis, B_z, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(x_axis) // 25),
            markersize=7, linewidth=lw, 
            label=f"MBGRN Mesh {i+1} ({total_cells:,} cells)"
        )

plt.xlabel('Angular Position (rad)', fontsize=s.label_size)
plt.ylabel('Airgap Flux Density $B_z$ (T)', fontsize=s.label_size)
plt.title('3D-MBGRN Airgap Axial Flux Density ($B_z$) Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='upper right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()