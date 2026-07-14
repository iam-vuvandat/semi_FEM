import paths
import numpy as np
import matplotlib.pyplot as plt

from src.core.storage.core.MotorIO import MotorIO
io = MotorIO()


re_solve = False
file_name = "motor_for_paper"
number_of_configuation = 5

file_name_array = []
for i in range(number_of_configuation):
    new_file_name = f"motor_for_paper{i}"
    file_name_array.append(new_file_name)
print(f"\033[94m{file_name_array}\033[0m")

if re_solve:
    motor_array = []
    for i in range(number_of_configuation):
        aft = io.load(path=file_name)
        motor_array.append(aft)

        aft.calculation_data.convergence_settings.max_iteration = 100
        aft.calculation_data.convergence_settings.max_relative_residual = 0.5 * 1e-2
        aft.calculation_data.convergence_settings.material_relax = 1.0
        aft.calculation_data.convergence_settings.damping_factor = 1.0
        aft.calculation_data.convergence_settings.relaxation_decay = 0.5

        aft.calculation_data.general_options.solve_cogging = False
        aft.calculation_data.general_options.solve_standard = True
        aft.calculation_data.general_options.solve_under_no_load = False
        aft.calculation_data.general_options.solve_on_load = True

        aft.just_changed('calculation_data')

    for i in range(number_of_configuation):
        aft = motor_array[i]
        
        aft.calculation_data.general_options.n_point = 16 + i * 8
        aft.just_changed('calculation_data')
        
        aft.adaptive_mesh_data.n_r_1 = 1 + i
        aft.adaptive_mesh_data.n_r_2 = 1 + i
        aft.adaptive_mesh_data.n_r_3 = 1 + i

        aft.adaptive_mesh_data.n_z_rotor_yoke = 1 + i
        aft.adaptive_mesh_data.n_z_magnet = 1 + i
        aft.adaptive_mesh_data.n_z_airgap = 3 + i * 2
        aft.adaptive_mesh_data.n_z_tooth_tip_1 = 1 + i
        aft.adaptive_mesh_data.n_z_tooth_tip_2 = 1 + i 
        aft.adaptive_mesh_data.n_z_tooth_body = 1 + i
        aft.adaptive_mesh_data.n_z_stator_yoke = 1 + i
        
        aft.just_changed('mesh')
        aft.update_mesh_by_calculation_data()

    table_data = []

    for idx, aft in enumerate(motor_array):
        aft.require('mesh')
        table_data.append((idx, aft.mesh.n_cells_r, aft.mesh.n_cells_t, aft.mesh.n_cells_z, aft.mesh.total_cells))

    print(f"{'Config':<8} | {'n_cells_r':<10} | {'n_cells_t':<10} | {'n_cells_z':<10} | {'total_cells':<12}")
    print("-" * 62)
    for row in table_data:
        print(f"{row[0]:<8} | {row[1]:<10} | {row[2]:<10} | {row[3]:<10} | {row[4]:<12}")

    config_index = [row[0] + 1 for row in table_data]
    total_elements = [row[4] for row in table_data]

    plt.figure()
    plt.plot(config_index, total_elements, marker='o', color='blue')
    plt.xlabel('Mesh Configuration Index')
    plt.ylabel('Total Mesh Cells')
    plt.title('Total Mesh Cells vs Configuration Index')
    plt.grid(True)
    plt.show()

    for i in range(number_of_configuation):
        aft = motor_array[i]
        aft.analysis_motor()
        io.save(motor=aft, path=file_name_array[i])

else: 
    motor_array = []
    for i in range(number_of_configuation):
        aft = io.load(path=file_name_array[i])
        motor_array.append(aft)