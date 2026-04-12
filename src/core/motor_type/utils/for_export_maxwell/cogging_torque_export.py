import paths
import numpy as np
import os

from src.core.solver.utils.duplicate_data import duplicate_data

def cogging_torque_export(motor, m3d):
    project_root = paths.configure_path()
    
    speed_rpm = getattr(motor.mechanical, 'shaft_speed', 3000)
    omega_m = (speed_rpm * 2 * np.pi) / 60 

    temp_dir = os.path.join(project_root, "data", "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    expressions = ["Moving1.Torque"]
    report_name = "Cogging_Torque_Report_FEM"
    csv_path = os.path.join(temp_dir, f"{report_name}.csv")

    m3d.post.create_report(
        expressions=expressions,
        setup_sweep_name="Setup1 : Transient",
        plot_name=report_name,
        plot_type="Rectangular Plot"
    )
    m3d.post.export_report_to_csv(temp_dir, report_name)

    with open(csv_path, 'r') as f:
        header = f.readline().strip().split(',')

    time_idx = -1
    time_multiplier = 1.0
    torque_idx = -1
    torque_multiplier = 1.0
    
    time_unit_map = {"[s]": 1.0, "[ms]": 1e-3, "[us]": 1e-6, "[ns]": 1e-9}
    torque_unit_map = {"[newtonmeter]": 1.0, "[mnewtonmeter]": 1e-3, "[unewtonmeter]": 1e-6}

    for i, col in enumerate(header):
        col_clean = col.replace('"', '').lower()
        
        if "time" in col_clean:
            time_idx = i
            for unit, mult in time_unit_map.items():
                if unit in col_clean:
                    time_multiplier = mult
                    break
        elif "moving1.torque" in col_clean:
            torque_idx = i
            for unit, mult in torque_unit_map.items():
                if unit in col_clean:
                    torque_multiplier = mult
                    break

    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    time_steps = raw_data[:, time_idx] * time_multiplier
    torque_data = raw_data[:, torque_idx] * torque_multiplier
    
    mechanical_power_data = torque_data * omega_m
    current_positions = time_steps * omega_m 

    combined_torque = np.vstack((torque_data, current_positions))
    combined_torque = combined_torque[:,:-1]
    
    combined_torque = duplicate_data(data = combined_torque, half_open_interval= True).duplicated_data
    

    motor.record.cogging_fem = combined_torque.copy()

    return None