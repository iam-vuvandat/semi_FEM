import paths
import numpy as np
import os

def torque_export(motor, m3d):
    project_root = paths.configure_path()
    
    speed_rpm = getattr(motor.mechanical, 'shaft_speed', 3000)
    omega_m = (speed_rpm * 2 * np.pi) / 60 

    temp_dir = os.path.join(project_root, "data", "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    expressions = ["Moving1.Torque"]
    report_name = "Torque_Report_FEM"
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
    
    # ĐÃ CẬP NHẬT: Thêm [ns] để xử lý dữ liệu nano giây
    time_unit_map = {"[s]": 1.0, "[ms]": 1e-3, "[us]": 1e-6, "[ns]": 1e-9}

    for i, col in enumerate(header):
        # Loại bỏ dấu ngoặc kép dư thừa từ Maxwell CSV
        col_clean = col.replace('"', '').lower()
        
        if "time" in col_clean:
            time_idx = i
            for unit, mult in time_unit_map.items():
                if unit in col_clean:
                    time_multiplier = mult
                    break
        elif "moving1.torque" in col_clean:
            torque_idx = i

    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    # Quy đổi: 4,000,000 [ns] * 1e-9 = 0.004 [s]
    time_steps = raw_data[:, time_idx] * time_multiplier
    torque_data = raw_data[:, torque_idx]
    
    mechanical_power_data = torque_data * omega_m
    current_positions = time_steps * omega_m 

    combined_torque = np.vstack((torque_data, current_positions))
    combined_torque = combined_torque[:,:-1]
    combined_power = np.vstack((mechanical_power_data, current_positions))
    combined_power = combined_power[:,:-1]

    motor.record.torque_fem = combined_torque.copy()
    motor.record.mechanical_power_fem = combined_power.copy()
    motor.record.average_mechanical_power_fem = np.mean(mechanical_power_data)

    return None