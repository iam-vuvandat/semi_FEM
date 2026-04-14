import paths
import numpy as np
import os

def torque_export(motor, m3d):
    project_root = paths.configure_path()
    
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

    # Lấy danh sách tất cả các tên report hiện có
    all_reports = list(oModule.GetAllReportNames())

    # Chỉ xóa nếu danh sách không trống
    if all_reports:
        oModule.DeleteReports(all_reports)
        print(f"Deleted existing reports: {all_reports}")
    else:
        print("No reports to delete. Skipping...")

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

    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    time_steps = raw_data[:, 0]
    torque_data = raw_data[:, 1]
    
    mechanical_power_data = torque_data * omega_m
    current_positions = time_steps * omega_m 

    combined_torque = np.vstack((torque_data, current_positions))
    half_open_interval = motor.maxwell_export_option.solver_option.half_open_interval
    if not half_open_interval:
        combined_torque = combined_torque[:,:-1]
    
    combined_torque[:-1,:] *= -1

    combined_power = np.vstack((mechanical_power_data, current_positions))
    

    motor.record.torque_fem = combined_torque.copy()
    motor.record.mechanical_power_fem = combined_power.copy()
    motor.record.average_mechanical_power_fem = np.mean(mechanical_power_data)

    print(f"Native Export: {report_name} processed.")
    return None