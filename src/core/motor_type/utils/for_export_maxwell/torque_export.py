import paths
import numpy as np
import os

def torque_export(motor, m3d):
    project_root = paths.configure_path()
    
    # Lấy tốc độ trục (RPM) và quy đổi sang vận tốc góc omega (rad/s)
    # Sử dụng cấu trúc motor.mechanical như trong hàm flux_linkage_export của bạn
    speed_rpm = getattr(motor.mechanical, 'shaft_speed', 3000)
    omega_m = (speed_rpm * 2 * np.pi) / 60 

    temp_dir = os.path.join(project_root, "data", "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    expressions = ["Moving1.Torque"]
    report_name = "Torque_Report_FEM"
    csv_path = os.path.join(temp_dir, f"{report_name}.csv")

    # 1. Tạo báo cáo và xuất CSV (tự động ghi đè)
    m3d.post.create_report(
        expressions=expressions,
        setup_sweep_name="Setup1 : Transient",
        plot_name=report_name,
        plot_type="Rectangular Plot"
    )
    m3d.post.export_report_to_csv(temp_dir, report_name)

    # 2. Đọc Header để xử lý Index và đơn vị
    with open(csv_path, 'r') as f:
        header = f.readline().strip().split(',')

    time_idx = -1
    time_multiplier = 1.0
    torque_idx = -1
    
    time_unit_map = {"[s]": 1.0, "[ms]": 1e-3, "[us]": 1e-6}

    for i, col in enumerate(header):
        col_clean = col.lower()
        if "time" in col_clean:
            time_idx = i
            for unit, mult in time_unit_map.items():
                if unit in col_clean:
                    time_multiplier = mult
                    break
        elif "moving1.torque" in col_clean:
            torque_idx = i

    # 3. Đọc dữ liệu số
    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    time_steps = raw_data[:, time_idx] * time_multiplier
    torque_data = raw_data[:, torque_idx]
    
    # 4. Tính toán các thành phần bổ sung
    # Công suất cơ học: P = T * omega_m (W)
    mechanical_power_data = torque_data * omega_m
    
    # Vị trí rotor (rad) để làm trục hoành cho đồ thị
    current_positions = time_steps * omega_m 

    # 5. Đóng gói và lưu vào record
    # Cấu trúc: [Dữ liệu, Vị trí rotor]
    combined_torque = np.vstack((torque_data, current_positions))
    combined_torque = combined_torque[:,:-1]
    combined_power = np.vstack((mechanical_power_data, current_positions))
    combined_power = combined_power[:,:-1]

    # Lưu kết quả FEM vào record
    motor.record.torque_fem = combined_torque.copy()
    motor.record.mechanical_power_fem = combined_power.copy()
    
    # Lưu thêm công suất trung bình để hàm plot_mechanical_power có thể hiển thị đường Average
    motor.record.average_mechanical_power_fem = np.mean(mechanical_power_data)

    return None