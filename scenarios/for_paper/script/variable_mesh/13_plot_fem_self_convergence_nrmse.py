import paths
import matplotlib.pyplot as plt
from src.core.storage.core.MotorIO import MotorIO
from src.core.solver.utils.get_waveform_nrmse import get_waveform_nrmse
from src.core.core_class.utils.for_data_processor.apply_jounal_style import apply_journal_style

io = MotorIO()
s = apply_journal_style()
fig_width, fig_height = 10, 10 / 1.5

number_of_configuation = 5
file_name_array = [f"motor_for_paper{i}" for i in range(number_of_configuation)]

motor_array = [io.load(path=fn) for fn in file_name_array]
reference_aft = motor_array[-1]
record_ref = reference_aft.record

if hasattr(record_ref, 'airgap_flux_density_fem') and record_ref.airgap_flux_density_fem is not None:
    fem_ref_B_z = record_ref.airgap_flux_density_fem
    fem_ref_psi = record_ref.flux_linkage_fem
    fem_ref_torque = record_ref.torque_fem

    fem_tets_array = []
    nrmse_fem_B_z = []
    nrmse_fem_psi = []
    nrmse_fem_torque = []

    for i in range(number_of_configuation):
        aft = motor_array[i]
        
        fem_pred_B_z = aft.record.airgap_flux_density_fem
        fem_pred_psi = aft.record.flux_linkage_fem
        fem_pred_torque = aft.record.torque_fem
        
        fem_tets = aft.record.mesh_data_fem.total_elements if hasattr(aft.record, 'mesh_data_fem') and aft.record.mesh_data_fem is not None else (i + 1)
        fem_tets_array.append(fem_tets)
        
        err_B_z = get_waveform_nrmse(data_true=fem_ref_B_z, data_pred=fem_pred_B_z, num_points=200, row_index=2)
        err_psi = get_waveform_nrmse(data_true=fem_ref_psi, data_pred=fem_pred_psi, num_points=200, row_index=2)
        err_torque = get_waveform_nrmse(data_true=fem_ref_torque, data_pred=fem_pred_torque, num_points=200, row_index=0)
        
        nrmse_fem_B_z.append(err_B_z)
        nrmse_fem_psi.append(err_psi)
        nrmse_fem_torque.append(err_torque)

    plt.figure(figsize=(fig_width, fig_height))
    plt.plot(fem_tets_array[:-1], nrmse_fem_B_z[:-1], color=s.colors[0], marker='o', linestyle='--', linewidth=2.5, markersize=9, label=r'FEM NRMSE of $B_z$')
    plt.plot(fem_tets_array[:-1], nrmse_fem_psi[:-1], color=s.colors[2], marker='s', linestyle='--', linewidth=2.5, markersize=9, label=r'FEM NRMSE of $\Psi_a$')
    plt.plot(fem_tets_array[:-1], nrmse_fem_torque[:-1], color=s.colors[1], marker='^', linestyle='--', linewidth=2.5, markersize=9, label='FEM NRMSE of Torque')
    plt.xlabel('Total FEM Tetrahedra Elements', fontsize=s.label_size)
    plt.ylabel('FEM Self-Convergence NRMSE (%)', fontsize=s.label_size)
    plt.title('3D-FEM Mesh Self-Convergence Rate Study', fontsize=s.title_size)
    plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
    plt.legend(frameon=True, loc='upper right', fontsize=s.legend_size)
    plt.tight_layout()
    plt.show()