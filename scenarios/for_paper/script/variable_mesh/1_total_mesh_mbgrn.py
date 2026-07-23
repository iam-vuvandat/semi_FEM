import paths
import matplotlib.pyplot as plt
from src.core.storage.core.MotorIO import MotorIO
from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style

io = MotorIO()
s = apply_journal_style()
fig_width, fig_height = 10, 10 / 1.5

number_of_configuation = 5
file_name_array = [f"motor_for_paper{i}" for i in range(number_of_configuation)]

total_elements = []
for i in range(number_of_configuation):
    aft = io.load(path=file_name_array[i])
    aft.require('mesh')
    total_elements.append(aft.mesh.total_cells)

config_index = list(range(1, number_of_configuation + 1))

plt.figure(figsize=(fig_width, fig_height))
plt.plot(config_index, total_elements, marker='o', color=s.colors[0], linewidth=2.0, markersize=8)
plt.xlabel('Mesh Configuration Index', fontsize=s.label_size)
plt.ylabel('Total Mesh Cells', fontsize=s.label_size)
plt.title('Total Mesh Cells vs Configuration Index', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.tight_layout()
plt.show()