import paths
import numpy as np
import os
from src.core.solver.utils.convert_to_dq import convert_to_dq
from src.core.solver.utils.periodic_derivative import periodic_derivative
from src.core.solver.utils.calculate_line_to_line_back_emf import calculate_line_to_line_back_emf

def flux_linkage_export(motor, m3d):
    # 1. Khởi tạo đường dẫn
    project_root = paths.configure_path()
    n_phase = motor.winding_data.phase
    poles = motor.geometry_data.rotor.pole_number
    speed_rpm = getattr(motor.mechanical, 'shaft_speed', 3000)
    omega_m = (speed_rpm * 2 * np.pi) / 60 

    temp_dir = os.path.join(project_root, "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    phase_map = ["A", "B", "C", "D", "E", "F"]
    y_expressions = [f"FluxLinkage(Phase{phase_map[i]})" for i in range(n_phase)]
    
    report_name = "Flux_Linkage_Report_FEM"
    csv_path = os.path.join(temp_dir, f"{report_name}.csv")

    # --- BỔ SUNG: Xóa file dữ liệu cũ trên ổ đĩa nếu tồn tại ---
    if os.path.exists(csv_path):
        try:
            os.remove(csv_path)
            print(f"Old file deleted: {csv_path}")
        except Exception as e:
            print(f"Warning: Could not delete old file {csv_path}. Error: {e}")

    oModule = m3d.odesign.GetModule("ReportSetup")

    # Lấy danh sách tất cả các tên report hiện có
    all_reports = list(oModule.GetAllReportNames())

    # Chỉ xóa nếu danh sách không trống
    if all_reports:
        oModule.DeleteReports(all_reports)
        print(f"Deleted existing reports: {all_reports}")
    else:
        print("No reports to delete. Skipping...")

    # 3. Tạo Report mới theo đúng cú pháp Record
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
            "Y Component:=", y_expressions
        ]
    )

    # 4. Xuất file CSV mới
    # Chuyển đổi đường dẫn sang dạng Maxwell hiểu được
    native_path = csv_path.replace("\\", "/")
    oModule.ExportToFile(report_name, native_path, False)

    # 5. Kiểm tra file mới đã được tạo chưa trước khi đọc
    if not os.path.exists(csv_path):
        print(f"\033[91mError: Maxwell failed to export new data to {csv_path}\033[0m")
        return

    # --- Đọc và xử lý dữ liệu như bình thường ---
    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    time_steps = raw_data[:, 0] 
    flux_phases = raw_data[:, 1:n_phase+1].T 
    
    n_steps = len(time_steps)
    current_positions = time_steps * omega_m 

    d_axis_flux = np.empty(n_steps)
    q_axis_flux = np.empty(n_steps)

    for i in range(n_steps):
        pos = current_positions[i]
        temp_val = np.empty((n_phase + 1, 1))
        temp_val[:-1, 0] = flux_phases[:, i]
        temp_val[-1, 0] = pos
        
        dq_data = convert_to_dq(temp_val, poles, pos)
        d_axis_flux[i] = dq_data[0, 0]
        q_axis_flux[i] = dq_data[1, 0]

    combined_data = np.vstack((d_axis_flux, q_axis_flux, flux_phases, current_positions))

    half_open_interval = motor.maxwell_export_option.solver_option.half_open_interval
    if not half_open_interval:
        combined_data = combined_data[:, :-1]

    back_emf = periodic_derivative(data=combined_data[2:], half_open_interval=True).derivative * omega_m
    back_emf_line = calculate_line_to_line_back_emf(data_numpy=back_emf)

    motor.record.flux_linkage_fem = combined_data.copy()
    motor.record.back_emf_fem = back_emf.copy()
    motor.record.back_emf_line_fem = back_emf_line.copy()
    
    print(f"\033[92mNative Export: Environment cleaned and fresh data processed.\033[0m")