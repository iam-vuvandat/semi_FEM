import numpy as np
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
    if hasattr(record, 'axial_force') and record.axial_force is not None:
        shaft_speed_i = (aft.mechanical_data.shaft_speed * np.pi * 2) / 60
        theta_data = record.axial_force[-1, :]
        time_ms = (theta_data / shaft_speed_i) * 1e3
        val_force = record.axial_force[0, :]
        total_cells = aft.mesh.total_cells
        lw = 2.5 if i == number_of_configuation - 1 else 1.5
        plt.plot(
            time_ms, val_force, 
            color=s.colors[i % len(s.colors)], 
            linestyle=s.linestyles[i % len(s.linestyles)],
            marker=s.markers[i % len(s.markers)],
            markevery=max(1, len(time_ms) // 25),
            markersize=7, linewidth=lw, 
            label=f"MBGRN Mesh {i+1} ({total_cells:,} cells)"
        )

plt.xlabel('Time (ms)', fontsize=s.label_size)
plt.ylabel('Axial Force (N)', fontsize=s.label_size)
plt.title('3D-MBGRN Axial Force Convergence Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='lower right', ncol=2, fontsize=s.legend_size)
plt.margins(x=0)
plt.tight_layout()
plt.show()