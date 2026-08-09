# post processing
import os
import paths
import matplotlib.pyplot as plt
from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style


def plot_fem_flux_linkage(file_name_array, io, figures_dir=None, mesh_indices=None):
    if figures_dir is None:
        root_dir = paths.configure_path()
        figures_dir = os.path.join(root_dir, "data", "repo", "figures")
    os.makedirs(figures_dir, exist_ok=True)

    s = apply_journal_style()
    fig_width, fig_height = 10, 10 / 1.5
    plt.figure(figsize=(fig_width, fig_height))

    is_last = lambda idx: idx == len(file_name_array) - 1

    for i, file_name in enumerate(file_name_array):
        if mesh_indices is not None and i not in mesh_indices:
            continue

        aft = io.load(path=file_name)
        record = aft.record
        
        if hasattr(record, 'flux_linkage_fem') and record.flux_linkage_fem is not None:
            data_fem = record.flux_linkage_fem
            x_fem = data_fem[-1, :]
            psi_a_fem = data_fem[2, :]
            
            lw = 2.5 if is_last(i) else 1.5
            line_color = 'black' if is_last(i) else s.colors[i % len(s.colors)]
            line_style = '-' if is_last(i) else '--'

            plt.plot(
                x_fem, psi_a_fem,
                color=line_color,
                linestyle=line_style,
                marker=s.markers[i % len(s.markers)],
                markevery=max(1, len(x_fem) // 25),
                markersize=7, linewidth=lw,
                label=f"Mesh {i + 1}"
            )
        del aft

    ax = plt.gca()
    plt.xlabel('Rotor Position (rad)', fontsize=s.label_size)
    plt.ylabel(r'Flux Linkage $\Psi_a$ (Wb)', fontsize=s.label_size)
    plt.title('3D-FEM Phase Flux Linkage Mesh Convergence Study', fontsize=s.title_size)
    plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
    
    handles, labels = ax.get_legend_handles_labels()
    if labels:
        plt.legend(
            handles, labels, 
            frameon=True, 
            loc='upper right', 
            ncol=3, 
            fontsize=s.legend_size - 2, 
            columnspacing=0.8, 
            handletextpad=0.4
        )
        
    plt.margins(x=0)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, '3d_fem_flux_linkage_convergence.png'), dpi=300, bbox_inches='tight')
    plt.show()