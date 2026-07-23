import paths
import matplotlib.pyplot as plt
from src.core.storage.core.MotorIO import MotorIO
from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style

io = MotorIO()
s = apply_journal_style()
fig_width, fig_height = 10, 10 / 1.5

number_of_configuation = 5
file_name_array = [f"motor_for_paper{i}" for i in range(number_of_configuation)]

max_element_lengths = []
units = "mm"

for i in range(number_of_configuation):
    aft = io.load(path=file_name_array[i])
    record = aft.record
    if hasattr(record, 'mesh_data_fem') and record.mesh_data_fem is not None:
        max_len = record.mesh_data_fem.max_element_length
        units = record.mesh_data_fem.unit
        max_element_lengths.append(max_len)
    else:
        max_element_lengths.append(0)

config_index = list(range(1, number_of_configuation + 1))

plt.figure(figsize=(fig_width, fig_height))
plt.plot(
    config_index, max_element_lengths, 
    marker='s', color=s.colors[1], linestyle='-', 
    linewidth=2.5, markersize=8, label='FEM Max Element Length'
)

plt.xlabel('Mesh Configuration Index', fontsize=s.label_size)
plt.ylabel(f'Maximum Element Length ({units})', fontsize=s.label_size)
plt.title('FEM Maximum Element Length vs Configuration Index', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.xticks(config_index)
plt.legend(frameon=True, loc='upper right', fontsize=s.legend_size)
plt.tight_layout()
plt.show()