# post processing
import os
import paths
import matplotlib.pyplot as plt
import numpy as np
from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style


def format_count(value):
    """Định dạng cho Số phần tử và Bậc tự do (giữ nguyên giá trị đơn vị 1)."""
    if value == 0:
        return '0'
    elif isinstance(value, float):
        return f'{value:.1f}'
    else:
        return f'{int(value)}'


def format_memory(value):
    """Định dạng cho Memory (giữ nguyên đơn vị MB)."""
    if value == 0:
        return '0'
    elif value < 10:
        return f'{value:.1f}'
    else:
        return f'{int(value)}'


def format_time_hours(seconds):
    """Định dạng cho Time (đổi từ giây sang giờ)."""
    hours = seconds / 3600.0
    if hours == 0:
        return '0'
    elif hours < 0.1:
        return f'{hours:.2f}'
    else:
        return f'{hours:.1f}'


def format_max_len(value):
    """Định dạng cho Actual Max Length (mm)."""
    if value == 0:
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
    b1 = ax.bar(indices - 1.0 * width_fem, fem_elements, width=width_fem, color=s.colors[1 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Number of Elements')
    b2 = ax.bar(indices, fem_matrix_sizes, width=width_fem, color=s.colors[2 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Matrix Size (Degrees of Freedom)')
    b3 = ax.bar(indices + 1.0 * width_fem, fem_memories, width=width_fem, color=s.colors[3 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Memory Usage (MB)')
    b4 = ax.bar(indices + 2.0 * width_fem, fem_times, width=width_fem, color=s.colors[7 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Execution Time (Hours)')

    bars_fem = [b0, b1, b2, b3, b4]
    formatters_fem = [format_max_len, format_count, format_count, format_memory, format_time_hours]
    vals_list_fem = [fem_max_lengths, fem_elements, fem_matrix_sizes, fem_memories, fem_times]

    for b, fmt, vals in zip(bars_fem, formatters_fem, vals_list_fem):
        labels = [fmt(v) for v in vals]
        # Cỡ chữ cố định 9pt
        ax.bar_label(b, labels=labels, padding=3, fontsize=9, rotation=90)

    max_val = max(max(fem_elements), max(fem_matrix_sizes))
    ax.set_ylim(0, max_val * 1.25)

    # Viền khung chữ nhật mỏng (linewidth=0.6)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.6)
        spine.set_color('black')

    ax.get_yaxis().set_visible(False)
    ax.set_xlabel('Mesh Configuration Index', fontsize=s.label_size)
    ax.legend(frameon=True, loc='upper left', ncol=2, fontsize=s.legend_size - 2, columnspacing=0.8, handletextpad=0.4)
    plt.title('All 3D-FEM Simulation Parameters', fontsize=s.title_size)
    ax.set_xticks(indices)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, '3d_fem_parameters_comparison.png'), dpi=300, bbox_inches='tight')
    plt.show()

    # ĐỒ THỊ 2: 3D-MBGRN
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    width_mbgrn = 0.2

    b1 = ax.bar(indices - 1.5 * width_mbgrn, mbgrn_elements, width=width_mbgrn, color=s.colors[0 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Number of Elements')
    b2 = ax.bar(indices - 0.5 * width_mbgrn, mbgrn_matrix_sizes, width=width_mbgrn, color=s.colors[4 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Matrix Size (Degrees of Freedom)')
    b3 = ax.bar(indices + 0.5 * width_mbgrn, mbgrn_memories, width=width_mbgrn, color=s.colors[5 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Memory Usage (MB)')
    b4 = ax.bar(indices + 1.5 * width_mbgrn, mbgrn_times, width=width_mbgrn, color=s.colors[6 % len(s.colors)], alpha=0.85, edgecolor='black', linewidth=1.0, label='Execution Time (Hours)')

    bars_mbgrn = [b1, b2, b3, b4]
    formatters_mbgrn = [format_count, format_count, format_memory, format_time_hours]
    vals_list_mbgrn = [mbgrn_elements, mbgrn_matrix_sizes, mbgrn_memories, mbgrn_times]

    for b, fmt, vals in zip(bars_mbgrn, formatters_mbgrn, vals_list_mbgrn):
        labels = [fmt(v) for v in vals]
        # Cỡ chữ cố định 9pt
        ax.bar_label(b, labels=labels, padding=3, fontsize=9, rotation=90)

    max_val_mbgrn = max(max(mbgrn_elements), max(mbgrn_matrix_sizes))
    ax.set_ylim(0, max_val_mbgrn * 1.25)

    # Viền khung chữ nhật mỏng (linewidth=0.6)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.6)
        spine.set_color('black')

    ax.get_yaxis().set_visible(False)
    ax.set_xlabel('Mesh Configuration Index', fontsize=s.label_size)
    ax.legend(frameon=True, loc='upper left', ncol=2, fontsize=s.legend_size - 2, columnspacing=0.8, handletextpad=0.4)
    plt.title('All 3D-MBGRN Simulation Parameters', fontsize=s.title_size)
    ax.set_xticks(indices)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, '3d_mbgrn_parameters_comparison.png'), dpi=300, bbox_inches='tight')
    plt.show()