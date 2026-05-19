import paths

import time 

from src.core.ansys_maxwell.rmxprt.setup.init_window import init_window
from src.core.ansys_maxwell.rmxprt.setup.open_rmxprt import init_rmxprt
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_machine.change_motor_type import change_motor_type

from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_stator.edit_stator import edit_stator
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_stator.edit_stator_core import edit_stator_core
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_stator.edit_stator_slot import edit_stator_slot
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_stator.edit_stator_winding import edit_stator_winding

from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_rotor.edit_rotor import edit_rotor
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_rotor.edit_magnet import edit_magnet

from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_solver.edit_solver import edit_solver
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.field_calculation_setup import field_calculation_setup
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.create_airgap_probe_line import create_airgap_probe_line

from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.edit_motion_setting import edit_motion_setting
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.edit_excitation import edit_excitation
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.setup_axial_force_calculation import setup_axial_force_calculation
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.assign_mesh import assign_mesh
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.solve_standard_step import solve_standard_step
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.solve_cogging_torque import solve_cogging_torque
from src.core.ansys_maxwell.rmxprt.motor_type.axial_flux_motor.edit_m3d.export_solution_data import export_solution_data

def export_to_rmxprt(motor = None):
    begin_time = time.perf_counter()
    # require property
    motor.require('geometry')

    # General init
    init_window()
    rmxprt = init_rmxprt(motor = motor)
    change_motor_type(rmxprt= rmxprt, motor = motor ,motor_type="Axial-Flux Rotor")

    # Edit Stator
    edit_stator(rmxprt = rmxprt, motor = motor)
    edit_stator_core(rmxprt= rmxprt, motor= motor)
    edit_stator_winding(rmxprt= rmxprt, motor=motor)
    edit_stator_slot(rmxprt= rmxprt, motor= motor)

    # Edit Rotor
    edit_rotor(rmxprt= rmxprt, motor= motor)
    edit_magnet(rmxprt= rmxprt, motor= motor)

    # Edit Solver 
    m3d= edit_solver(rmxprt= rmxprt, motor= motor)
    field_calculation_setup(m3d = m3d)
    create_airgap_probe_line(m3d = m3d, motor = motor)

    # edit m3d
    edit_motion_setting(m3d = m3d, motor = motor)
    edit_excitation(m3d = m3d, motor = motor)
    setup_axial_force_calculation(m3d = m3d)
    assign_mesh(m3d= m3d, motor= motor)

    # solve and export solution data
    solve_standard_step(m3d= m3d, motor= motor)
    
    solve_cogging_torque(m3d= m3d, motor= motor)
  

    # close after completed
    if motor.maxwell_export_option.solver_option.close_after_completed is True:
        init_window()

    end_time =  time.perf_counter()
    total_time = end_time - begin_time
    motor.record.total_time_fem = total_time
    print("Time simulation (FEM):",total_time)

if __name__ == "__main__":
    from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1
    aft = AxialFluxMotorType1()
    aft.export_to_rmxprt()
    