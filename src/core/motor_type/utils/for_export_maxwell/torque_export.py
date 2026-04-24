import paths
import numpy as np
import os

def torque_export(motor, m3d):
    project_root = paths.configure_path()
    
    # Sử dụng omega chuẩn từ đối tượng mechanical
    omega_m = motor.mechanical.omega

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
        ["Time:=", ["All"], "fractions:=", ["Nominal"], "halfAxial:=", ["Nominal"], 
         "endRegion:=", ["Nominal"], "delta:=", ["Nominal"], "conds:=", ["Nominal"], 
         "R1:=", ["Nominal"], "Le1:=", ["Nominal"]], 
        ["X Component:=", "Time", "Y Component:=", [expression]]
    )

    oModule.ExportToFile(report_name, csv_path.replace("\\", "/"), False)

    if not os.path.exists(csv_path):
        return None

    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    time_steps = raw_data[:, 0]
    torque_data = raw_data[:, 1]
    
    # 1. Xác định offset đồng bộ hóa từ geometry_option
    offset = motor.geometry_data.geometry_option.rotor_mechanical_synchronized
    
    # 2. Tính toán chuẩn góc duy nhất (đã bao gồm offset)
    current_positions = (time_steps * omega_m) + offset

    # 3. Tính toán công suất cơ học dựa trên torque và omega
    mechanical_power_data = torque_data * omega_m

    # 4. Lưu trữ theo quy ước: Hàng 0 là giá trị vật lý, Hàng cuối là Position
    combined_torque = np.vstack((torque_data, current_positions))
    combined_power = np.vstack((mechanical_power_data, current_positions))

    motor.record.torque_fem = combined_torque.copy()
    motor.record.mechanical_power_fem = combined_power.copy()
    motor.record.average_mechanical_power_fem = np.mean(mechanical_power_data)

    print(f"\033[92mSuccess: Torque and Power exported and offset by {offset:.4f} rad\033[0m")
    return None