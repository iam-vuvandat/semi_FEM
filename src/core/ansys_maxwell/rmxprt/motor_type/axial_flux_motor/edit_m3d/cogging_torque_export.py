import paths
import numpy as np
import os

def cogging_torque_export(motor, m3d):
    project_root = paths.configure_path()
    omega_m = motor.mechanical.omega
    temp_dir = os.path.join(project_root, "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    expression = "Moving1.Torque"
    report_name = "Cogging_Report_FEM"
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
    time_unit_map = {"[s]": 1.0, "[ms]": 1e-3, "[us]": 1e-6, "[ns]": 1e-9, "[min]": 60.0, "[h]": 3600.0}
    torque_unit_map = {"mNewtonMeter": 1e-3, "NewtonMeter": 1.0, "[N.m]": 1.0, "[Nm]": 1.0, "[kN.m]": 1000.0, "[kNm]": 1000.0, "[kn.m]": 1000.0, "[knm]": 1000.0, "[mN.m]": 1e-3, "[mNm]": 1e-3, "[kgf.cm]": 0.0980665}
    
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

    motor.record.cogging_fem = np.vstack((torque_val, current_positions))
    print(f"\033[92mSuccess: Cogging Torque exported and scaled (Offset: {offset:.4f} rad)\033[0m")