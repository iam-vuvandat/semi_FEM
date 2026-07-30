# post processing
import os
import paths
import matplotlib.pyplot as plt
import numpy as np
from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style


def format_label(value):
    if value >= 1e6:
        return f'{value/1e6:.2f}M'
    elif value >= 1e3:
        return f'{value/1e3:.1f}k'
    elif value == 0:
        return '0'
    elif value < 10:
        return f'{value:.1f}'
    else:
        return f'{int(value)}'


def plot_mesh_elements_vs_config(file_name_array, io, figures_dir=None):
    if figures_dir is None:
        root_dir = paths.configure_path()
        figures_dir = os.path.join(root_dir, "data", "repo", "figures")
    os.makedirs(figures_dir, exist_ok=True)

    s = apply_journal_style()
    fig_width, fig_height = 10, 10 / 1.5
    indices = np.arange(1, len(file_name_array) + 1)

    mbgrn_elements, mbgrn_matrix_sizes, mbgrn_memories, mbgrn_times = [], [], [], []
    fem_max_lengths, fem_elements, fem_matrix_sizes, fem_memories, fem_times = [], [], [], [], []

    for file_name in file_name_array:
        aft = io.load(path=file_name)
        record = aft.record
        
        aft.require('mesh')
        mbgrn_cells = aft.mesh.total_cells if hasattr(aft, 'mesh') and aft.mesh is not None else 0
        mbgrn_elements.append(mbgrn_cells)
        mbgrn_matrix_sizes.append(getattr(record, 'matrix_size', 0))
        mbgrn_memories.append(getattr(record, 'memory_used', 0.0))
        mbgrn_times.append(getattr(record, 'time_solved', 0.0))
        
        # Đọc trực tiếp max_element_length thực tế từ record.mesh_data_fem[cite: 11]
        fem_max_len = record.mesh_data_fem.max_element_length if hasattr(record, 'mesh_data_fem') and record.mesh_data_fem is not None else 0.0
        fem_max_lengths.append(fem_max_len)

        fem_tets = record.mesh_data_fem.total_elements if hasattr(record, 'mesh_data_fem') and record.mesh_data_fem is not None else getattr(record, 'total_elements_fem', 0)
        fem_elements.append(fem_tets)
        fem_matrix_sizes.append(getattr(record, 'matrix_size_fem', 0))
        fem_memories.append(getattr(record, 'memory_used_fem', 0.0))
        fem_times.append(getattr(record, 'total_time_fem', 0.0))
        
        del aft

    # ĐỒ THỊ 1: 3D-FEM (5 cột thông số)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    width_fem = 0.16

    b0 = ax.bar(indices - 2.0 * width_fem, fem_max_lengths, width=width_fem, color=s.colors[0 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Actual Max Length (mm)')
    b1 = ax.bar(indices - 1.0 * width_fem, fem_elements, width=width_fem, color=s.colors[1 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Tetrahedra')
    b2 = ax.bar(indices, fem_matrix_sizes, width=width_fem, color=s.colors[2 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Matrix Size')
    b3 = ax.bar(indices + 1.0 * width_fem, fem_memories, width=width_fem, color=s.colors[3 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Memory (MB)')
    b4 = ax.bar(indices + 2.0 * width_fem, fem_times, width=width_fem, color=s.colors[7 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Time (s)')

    bars = [b0, b1, b2, b3, b4]
    vals_list = [fem_max_lengths, fem_elements, fem_matrix_sizes, fem_memories, fem_times]

    for b, vals in zip(bars, vals_list):
        labels = [format_label(v) for v in vals]
        ax.bar_label(b, labels=labels, padding=3, fontsize=s.legend_size - 2, rotation=90)

    ax.get_yaxis().set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_xlabel('Mesh Configuration Index', fontsize=s.label_size)
    ax.legend(frameon=True, loc='upper left', ncol=3, fontsize=s.legend_size - 2, columnspacing=0.8, handletextpad=0.4)
    plt.title('All 3D-FEM Simulation Parameters', fontsize=s.title_size)
    ax.set_xticks(indices)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, '3d_fem_parameters_comparison.png'), dpi=300, bbox_inches='tight')
    plt.show()

    # ĐỒ THỊ 2: 3D-MBGRN
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    width_mbgrn = 0.2

    b1 = ax.bar(indices - 1.5 * width_mbgrn, mbgrn_elements, width=width_mbgrn, color=s.colors[0 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Cells')
    b2 = ax.bar(indices - 0.5 * width_mbgrn, mbgrn_matrix_sizes, width=width_mbgrn, color=s.colors[4 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Matrix Size')
    b3 = ax.bar(indices + 0.5 * width_mbgrn, mbgrn_memories, width=width_mbgrn, color=s.colors[5 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Memory (MB)')
    b4 = ax.bar(indices + 1.5 * width_mbgrn, mbgrn_times, width=width_mbgrn, color=s.colors[6 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Time (s)')

    for b, vals in zip([b1, b2, b3, b4], [mbgrn_elements, mbgrn_matrix_sizes, mbgrn_memories, mbgrn_times]):
        labels = [format_label(v) for v in vals]
        ax.bar_label(b, labels=labels, padding=3, fontsize=s.legend_size - 2, rotation=90)

    ax.get_yaxis().set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.set_xlabel('Mesh Configuration Index', fontsize=s.label_size)
    ax.legend(frameon=True, loc='upper left', ncol=2, fontsize=s.legend_size - 2, columnspacing=0.8, handletextpad=0.4)
    plt.title('All 3D-MBGRN Simulation Parameters', fontsize=s.title_size)
    ax.set_xticks(indices)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, '3d_mbgrn_parameters_comparison.png'), dpi=300, bbox_inches='tight')
    plt.show()