import paths
import numpy as np
import os

def torque_export(motor, m3d):
    project_root = paths.configure_path()
    omega_m = motor.mechanical.omega
    temp_dir = os.path.join(project_root, "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    expression = "Moving1.Torque"
    report_name = "Torque_Report_FEM"
    csv_path = os.path.join(temp_dir, f"{report_name}.csv")

    oModule = m3d.odesign.GetModule("ReportSetup")
    all_reports = list(oModule.GetAllReportNames())
    if all_reports:
        oModule.DeleteReports(all_reports)

    oModule.CreateReport(report_name, "Transient", "Rectangular Plot", "Setup1 : Transient", 
        ["Domain:=", "Sweep"], ["Time:=", ["All"]], 
        ["X Component:=", "Time", "Y Component:=", [expression]]
    )
    oModule.ExportToFile(report_name, csv_path.replace("\\", "/"), False)

    with open(csv_path, 'r') as f:
        header = f.readline().strip().split(',')

    time_idx, torque_idx = 0, 1
    time_mult, torque_mult = 1.0, 1.0
    time_unit_map = {"[s]": 1.0, "[ms]": 1e-3, "[us]": 1e-6}
    torque_unit_map = {"[n.m]": 1.0, "[nm]": 1.0}

    for i, col in enumerate(header):
        col_clean = col.replace('"', '').lower()
        if "time" in col_clean:
            time_idx = i
            for unit, mult in time_unit_map.items():
                if unit in col_clean: time_mult = mult; break
        elif "torque" in col_clean:
            torque_idx = i
            for unit, mult in torque_unit_map.items():
                if unit in col_clean: torque_mult = mult; break

    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    time_steps = raw_data[:, time_idx] * time_mult
    torque_val = raw_data[:, torque_idx] * torque_mult
    
    offset = motor.geometry_data.geometry_option.rotor_mechanical_synchronized
    current_positions = (time_steps * omega_m) + offset
    mechanical_power = torque_val * omega_m

    motor.record.torque_fem = np.vstack((torque_val, current_positions))
    motor.record.mechanical_power_fem = np.vstack((mechanical_power, current_positions))
    motor.record.average_mechanical_power_fem = np.mean(mechanical_power)
    print(f"\033[92mSuccess: Torque exported and scaled (Offset: {offset:.4f} rad)\033[0m")