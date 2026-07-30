# post processing
import os
import paths
import matplotlib.pyplot as plt
import numpy as np
from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse


def plot_mbgrn_self_convergence(file_name_array, io, figures_dir=None):
    if figures_dir is None:
        root_dir = paths.configure_path()
        figures_dir = os.path.join(root_dir, "data", "repo", "figures")
    os.makedirs(figures_dir, exist_ok=True)

    s = apply_journal_style()
    fig_width, fig_height = 10, 10 / 1.5
    
    aft_ref = io.load(path=file_name_array[-1])
    record_ref = aft_ref.record
    
    torque_true = record_ref.torque if hasattr(record_ref, 'torque') and record_ref.torque is not None else None
    flux_true = record_ref.flux_linkage if hasattr(record_ref, 'flux_linkage') and record_ref.flux_linkage is not None else None
    bgap_true = record_ref.airgap_flux_density if hasattr(record_ref, 'airgap_flux_density') and record_ref.airgap_flux_density is not None else None
    
    del aft_ref

    elements_count = []
    torque_nrmse_list = []
    flux_nrmse_list = []
    bgap_nrmse_list = []

    for file_name in file_name_array:
        aft = io.load(path=file_name)
        aft.require('mesh')
        cells = aft.mesh.total_cells if hasattr(aft, 'mesh') and aft.mesh is not None else 0
        elements_count.append(cells)
        
        record = aft.record
        
        if torque_true is not None and hasattr(record, 'torque') and record.torque is not None:
            nrmse_val = get_waveform_nrmse(torque_true, record.torque, num_points=100, row_index=0)
            torque_nrmse_list.append(nrmse_val)
        else:
            torque_nrmse_list.append(0.0)
            
        if flux_true is not None and hasattr(record, 'flux_linkage') and record.flux_linkage is not None:
            nrmse_val = get_waveform_nrmse(flux_true, record.flux_linkage, num_points=100, row_index=2)
            flux_nrmse_list.append(nrmse_val)
        else:
            flux_nrmse_list.append(0.0)

        if bgap_true is not None and hasattr(record, 'airgap_flux_density') and record.airgap_flux_density is not None:
            nrmse_val = get_waveform_nrmse(bgap_true, record.airgap_flux_density, num_points=100, row_index=2)
            bgap_nrmse_list.append(nrmse_val)
        else:
            bgap_nrmse_list.append(0.0)

        del aft

    plt.figure(figsize=(fig_width, fig_height))

    # Trục hoành X: elements_count (Số phần tử)
    plt.plot(
        elements_count, torque_nrmse_list,
        color=s.colors[1 % len(s.colors)], 
        linestyle=s.linestyles[1 % len(s.linestyles)], 
        marker=s.markers[1 % len(s.markers)],
        markersize=8, linewidth=2.0, label='Torque NRMSE'
    )
    plt.plot(
        elements_count, flux_nrmse_list,
        color=s.colors[2 % len(s.colors)], 
        linestyle=s.linestyles[2 % len(s.linestyles)], 
        marker=s.markers[2 % len(s.markers)],
        markersize=8, linewidth=2.0, label=r'$\Psi_a$ NRMSE'
    )
    plt.plot(
        elements_count, bgap_nrmse_list,
        color=s.colors[3 % len(s.colors)], 
        linestyle=s.linestyles[3 % len(s.linestyles)], 
        marker=s.markers[3 % len(s.markers)],
        markersize=8, linewidth=2.0, label=r'$B_z$ NRMSE'
    )

    plt.xlabel('Total MBGRN Cells', fontsize=s.label_size)
    plt.ylabel('NRMSE (%)', fontsize=s.label_size)
    plt.title('3D-MBGRN Multi-Parameter NRMSE Self-Convergence', fontsize=s.title_size)
    plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
    plt.legend(frameon=True, loc='upper right', ncol=3, fontsize=s.legend_size - 2, columnspacing=0.8, handletextpad=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, '3d_mbgrn_self_convergence.png'), dpi=300, bbox_inches='tight')
    plt.show()