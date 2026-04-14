import paths
import numpy as np
import os
from src.core.solver.utils.duplicate_data import duplicate_data

def cogging_torque_export(motor, m3d):
    # 1. Khởi tạo đường dẫn và thông số cơ bản
    project_root = paths.configure_path()
    
    speed_rpm = getattr(motor.mechanical, 'shaft_speed', 3000)
    omega_m = (speed_rpm * 2 * np.pi) / 60 

    temp_dir = os.path.join(project_root, "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    expression = "Moving1.Torque"
    report_name = "Cogging_Torque_Report_FEM"
    csv_path = os.path.join(temp_dir, f"{report_name}.csv")

    # --- BỔ SUNG: Xóa file dữ liệu cũ trên ổ đĩa để tránh đọc nhầm dữ liệu rác ---
    if os.path.exists(csv_path):
        try:
            os.remove(csv_path)
        except Exception as e:
            print(f"Warning: Could not delete old cogging file: {e}")

    # 2. Truy cập Native Module và dọn dẹp môi trường Report
    oModule = m3d.odesign.GetModule("ReportSetup")

    # Lấy danh sách tất cả các tên report hiện có
    all_reports = list(oModule.GetAllReportNames())

    # Chỉ xóa nếu danh sách không trống
    if all_reports:
        oModule.DeleteReports(all_reports)
        print(f"Deleted existing reports: {all_reports}")
    else:
        print("No reports to delete. Skipping...")

    # 3. Tạo Report Cogging Torque theo cú pháp Native Record
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

    # 4. Xuất file CSV bằng lệnh Native ExportToFile
    native_path = csv_path.replace("\\", "/")
    oModule.ExportToFile(report_name, native_path, False)

    # 5. Kiểm tra và đọc dữ liệu từ file mới
    if not os.path.exists(csv_path):
        print(f"\033[91mError: Native export failed to create {csv_path}\033[0m")
        return None

    # Skip header=1: Maxwell native export luôn để Time ở cột 0 và Torque ở cột 1
    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    # Kiểm tra nếu file rỗng
    if raw_data.size == 0:
        print(f"\033[91mError: Exported CSV is empty.\033[0m")
        return None

    time_steps = raw_data[:, 0]
    torque_data = raw_data[:, 1]
    
    current_positions = time_steps * omega_m 

    # Đóng gói dữ liệu ban đầu
    combined_torque = np.vstack((torque_data, current_positions))
    
    # Cắt bỏ điểm cuối (Half-open interval) để tránh lặp điểm khi duplicate
    half_open_interval = motor.maxwell_export_option.solver_option.half_open_interval
    if not half_open_interval:
        combined_torque = combined_torque[:, :-1]

    combined_torque[:-1,:] *= -1
    
    # --- XỬ LÝ ĐỐI XỨNG: Nhân bản dữ liệu Cogging Torque ---
    # Sử dụng duplicate_data để mở rộng từ 1 chu kỳ cogging ra toàn bộ vòng quay
    combined_torque = duplicate_data(data=combined_torque, half_open_interval=True).duplicated_data

    # 6. Lưu kết quả vào motor record
    motor.record.cogging_fem = combined_torque.copy()

    print(f"\033[92mNative Export: {report_name} exported and duplicated successfully.\033[0m")

    return None