import paths
import numpy as np
import os

from src.core.solver.utils.calculate_mechanical_power import calculate_mechanical_power
from src.core.solver.utils.alternetive_first_point import alternetive_first_point

def torque_export(motor, m3d):
    project_root = paths.configure_path()
    
    use_alt_point = motor.maxwell_export_option.solver_option.alternetive_first_point

    speed_rpm = getattr(motor.mechanical, 'shaft_speed', 3000)
    omega_m = (speed_rpm * 2 * np.pi) / 60 

    temp_dir = os.path.join(project_root, "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    expression = "Moving1.Torque"
    report_name = "Torque_Report_FEM"
    csv_path = os.path.join(temp_dir, f"{report_name}.csv")

    if os.path.exists(csv_path):
        try:
            os.remove(csv_path)
        except Exception as e:
            print(f"Warning: Could not delete {csv_path}: {e}")

    oModule = m3d.odesign.GetModule("ReportSetup")
    
    all_reports = list(oModule.GetAllReportNames())
    if all_reports:
        oModule.DeleteReports(all_reports)

    oModule.CreateReport(report_name, "Transient", "Rectangular Plot", "Setup1 : Transient", 
        ["Domain:=", "Sweep"], 
        [
            "Time:=", ["All"],
            "fractions:=", ["Nominal"],
            "halfAxial:=", ["Nominal"],
            "endRegion:=", ["Nominal"],
            "delta:=", ["Nominal"],
            "conds:=", ["Nominal"],
            "R1:=", ["Nominal"],
            "Le1:=", ["Nominal"]
        ], 
        [
            "X Component:=", "Time",
            "Y Component:=", [expression]
        ]
    )

    native_path = csv_path.replace("\\", "/")
    oModule.ExportToFile(report_name, native_path, False)

    if not os.path.exists(csv_path):
        return None

    with open(csv_path, 'r') as f:
        header = f.readline().strip().split(',')

    time_idx = 0
    time_multiplier = 1.0
    torque_idx = 1
    torque_multiplier = 1.0
    
    time_unit_map = {"[s]": 1.0, "[ms]": 1e-3, "[us]": 1e-6}
    torque_unit_map = {"[newtonmeter]": 1.0, "[mnewtonmeter]": 1e-3}

    for i, col in enumerate(header):
        col_clean = col.replace('"', '').lower()
        if "time" in col_clean:
            time_idx = i
            for unit, mult in time_unit_map.items():
                if unit in col_clean:
                    time_multiplier = mult
                    break
        elif "torque" in col_clean:
            torque_idx = i
            for unit, mult in torque_unit_map.items():
                if unit in col_clean:
                    torque_multiplier = mult
                    break

    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    time_steps = raw_data[:, time_idx] * time_multiplier
    torque_data = raw_data[:, torque_idx] * torque_multiplier * -1
    
    current_positions = time_steps * omega_m 

    # Ghep du lieu thanh mang 2D truoc khi xu ly dong bo va cat diem
    combined_torque = np.vstack((torque_data, current_positions))

    if use_alt_point:
        # Dong bo diem dau va xoa diem cuoi de tao khoang nua mo
        combined_torque = alternetive_first_point(data = combined_torque,
                                                remove_last_point = True,
                                                last_row_is_position = True)
    else:
        # Neu khong dung alt_point, van phai cat bo diem cuoi de tinh toan trung binh chinh xac
        combined_torque = combined_torque[:, :-1]

    # Tinh toan cong suat co hoc tu du lieu torque da xu ly
    power_result = calculate_mechanical_power(torque_data = combined_torque, speed_rpm = speed_rpm)

    motor.record.torque_fem = combined_torque.copy()
    motor.record.mechanical_power_fem = power_result.mechanical_data.copy()
    motor.record.average_mechanical_power_fem = power_result.average_mechanical_data

    print(f"Native Export: {report_name} processed.")
    return None