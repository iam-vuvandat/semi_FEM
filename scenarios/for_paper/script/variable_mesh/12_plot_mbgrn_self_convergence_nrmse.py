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
total_elements = [aft.mesh.total_cells for aft in motor_array]

reference_aft = motor_array[-1]
mbgrn_ref_B_z = reference_aft.record.airgap_flux_density
mbgrn_ref_psi = reference_aft.record.flux_linkage
mbgrn_ref_torque = reference_aft.record.torque

nrmse_mbgrn_B_z = []
nrmse_mbgrn_psi = []
nrmse_mbgrn_torque = []

for i in range(number_of_configuation):
    aft = motor_array[i]
    
    data_pred_B_z = aft.record.airgap_flux_density
    data_pred_psi = aft.record.flux_linkage
    data_pred_torque = aft.record.torque
    
    err_B_z = get_waveform_nrmse(data_true=mbgrn_ref_B_z, data_pred=data_pred_B_z, num_points=200, row_index=2)
    err_psi = get_waveform_nrmse(data_true=mbgrn_ref_psi, data_pred=data_pred_psi, num_points=200, row_index=2)
    err_torque = get_waveform_nrmse(data_true=mbgrn_ref_torque, data_pred=data_pred_torque, num_points=200, row_index=0)
    
    nrmse_mbgrn_B_z.append(err_B_z)
    nrmse_mbgrn_psi.append(err_psi)
    nrmse_mbgrn_torque.append(err_torque)

plt.figure(figsize=(fig_width, fig_height))
plt.plot(total_elements[:-1], nrmse_mbgrn_B_z[:-1], color=s.colors[0], marker='o', linestyle='-', linewidth=2.5, markersize=9, label=r'NRMSE of $B_z$')
plt.plot(total_elements[:-1], nrmse_mbgrn_psi[:-1], color=s.colors[2], marker='s', linestyle='-', linewidth=2.5, markersize=9, label=r'NRMSE of $\Psi_a$')
plt.plot(total_elements[:-1], nrmse_mbgrn_torque[:-1], color=s.colors[1], marker='^', linestyle='-', linewidth=2.5, markersize=9, label='NRMSE of Torque')
plt.xlabel('Total MBGRN Elements ($Q_E$)', fontsize=s.label_size)
plt.ylabel('MBGRN Self-Convergence NRMSE (%)', fontsize=s.label_size)
plt.title('3D-MBGRN Mesh Self-Convergence Rate Study', fontsize=s.title_size)
plt.grid(True, linestyle='-', linewidth=s.grid_linewidth)
plt.legend(frameon=True, loc='upper right', fontsize=s.legend_size)
plt.tight_layout()
plt.show()