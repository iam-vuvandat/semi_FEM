import paths
import numpy as np
import os
from src.core.solver.utils.alternetive_first_point import alternetive_first_point

def cogging_torque_export(motor, m3d):
    """
    Xuất dữ liệu Cogging Torque từ Maxwell và đồng bộ hóa góc chuẩn.
    Loại bỏ duplicate_data để giữ nguyên khung thời gian mô phỏng thực tế.
    """
    project_root = paths.configure_path()
    
    # Sử dụng omega chuẩn từ đối tượng mechanical
    omega_m = motor.mechanical.omega

    temp_dir = os.path.join(project_root, "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    expression = "Moving1.Torque"
    report_name = "Cogging_Torque_Report_FEM"
    csv_path = os.path.join(temp_dir, f"{report_name}.csv")

    if os.path.exists(csv_path):
        try:
            os.remove(csv_path)
        except Exception as e:
            print(f"Warning: Could not delete old cogging file: {e}")

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

    oModule.ExportToFile(report_name, csv_path.replace("\\", "/"), False)

    if not os.path.exists(csv_path):
        print(f"\033[91mError: Native export failed to create {csv_path}\033[0m")
        return None

    with open(csv_path, 'r') as f:
        header = f.readline().strip().split(',')

    time_idx = 0
    time_multiplier = 1.0
    torque_idx = 1
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
        elif "torque" in col_clean:
            torque_idx = i
            for unit, mult in torque_unit_map.items():
                if unit in col_clean:
                    torque_multiplier = mult
                    break

    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    if raw_data.size == 0:
        print(f"\033[91mError: Exported CSV is empty.\033[0m")
        return None

    # Chuyển đổi đơn vị chuẩn
    time_steps = raw_data[:, time_idx] * time_multiplier
    torque_data = raw_data[:, torque_idx] * torque_multiplier
    
    # 1. Xác định offset đồng bộ hóa
    offset = motor.geometry_data.geometry_option.rotor_mechanical_synchronized
    
    # 2. Tính toán chuẩn góc duy nhất đã offset
    current_positions = (time_steps * omega_m) + offset

    # 3. Kết hợp dữ liệu (Hàng cuối cùng là Position)
    combined_torque = np.vstack((torque_data, current_positions))
    
    # Gán trực tiếp vào record mà không nhân bản dữ liệu
    motor.record.cogging_fem = combined_torque.copy()

    print(f"\033[92mSuccess: Cogging torque exported and offset by {offset:.4f} rad (No duplication)\033[0m")
    return None