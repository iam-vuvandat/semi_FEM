import paths
import math
import numpy as np 
import matplotlib.pyplot as plt
from src.core.storage.core.MotorIO import MotorIO
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
pi = math.pi
io = MotorIO()

# Initial setup
from src.core.ansys_maxwell.rmxprt.setup.init_window import init_window
init_window()

# Load motor
file_name = "motor_for_paper" 
aft = io.load(path=file_name)

# adaptive_mesh_data
aft.adaptive_mesh_data.n_z_tooth_tip_2 = 2
aft.adaptive_mesh_data.n_z_tooth_body = 2
aft.adaptive_mesh_data.n_z_stator_yoke = 2
aft.adaptive_mesh_data.n_z_out_air = 1
aft.adaptive_mesh_data.use_symmetry_factor = True
aft.adaptive_mesh_data.periodic_boundary = True
aft.just_changed('mesh')

aft.calculation_data.general_options.n_point = 3
aft.calculation_data.general_options.solve_cogging = True
aft.calculation_data.general_options.solve_standard = True
aft.calculation_data.general_options.solve_under_no_load = True
aft.calculation_data.general_options.solve_on_load = True

aft.maxwell_export_option.custom_option.mesh_setting.length_band_element_length = 10
aft.maxwell_export_option.custom_option.mesh_setting.length_coil_element_length = 10
aft.maxwell_export_option.custom_option.mesh_setting.length_mag_element_length = 10
aft.maxwell_export_option.custom_option.mesh_setting.length_main_element_length = 10
aft.maxwell_export_option.custom_option.mesh_setting.length_region_element_length = 10

aft.export_to_rmxprt()
aft.analysis_motor()


dp = aft.data_processor
dp.plot_airgap_flux_density()
dp.plot_airgap_flux_density_no_load()
dp.plot_flux_linkage(horizontal_axis="time", show_fem=True, show_dq= False, show_all_phase= True)
dp.plot_flux_linkage_no_load(horizontal_axis="time", show_fem=True, show_dq= False, show_all_phase= True)
dp.plot_back_emf(horizontal_axis="time", show_fem=True, show_all_phases= True)
dp.plot_back_emf_no_load(horizontal_axis="time", show_fem=True, show_all_phases= True)
dp.plot_torque(horizontal_axis="time", show_fem=True)
dp.plot_mechanical_power(horizontal_axis="time", show_fem=True)
dp.plot_cogging_torque(horizontal_axis="time", show_fem=True, revert = False, num_periods= 5)
dp.plot_axial_force(horizontal_axis="time", show_fem=True)
dp.plot_axial_force_no_load(horizontal_axis="time", show_fem=True)
dp.plot_current()
                                                                                                                                                                                                                  