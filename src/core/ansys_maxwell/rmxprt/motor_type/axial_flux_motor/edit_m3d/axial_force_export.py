import paths
import numpy as np
import os
from src.core.solver.utils.alternetive_first_point import alternetive_first_point

def axial_force_export(motor, m3d):
    project_root = paths.configure_path()
    
    use_alt_point = motor.maxwell_export_option.solver_option.alternetive_first_point

    speed_rpm = getattr(motor.mechanical, 'shaft_speed', 3000)
    omega_m = (speed_rpm * 2 * np.pi) / 60 

    temp_dir = os.path.join(project_root, "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    expression = "Axial_Force.Force_z"
    report_name = "Axial_Force_Report_FEM"
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
    force_idx = 1
    force_multiplier = 1.0
    
    time_unit_map = {"[s]": 1.0, "[ms]": 1e-3, "[us]": 1e-6}
    force_unit_map = {"[newton]": 1.0, "[mnewton]": 1e-3, "[knewton]": 1e3}
    
    for i, col in enumerate(header):
        col_clean = col.replace('"', '').lower()
        if "time" in col_clean:
            time_idx = i
            for unit, mult in time_unit_map.items():
                if unit in col_clean:
                    time_multiplier = mult
                    break
        elif "force" in col_clean:
            force_idx = i
            for unit, mult in force_unit_map.items():
                if unit in col_clean:
                    force_multiplier = mult
                    break

    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    time_steps = raw_data[:, time_idx] * time_multiplier
    force_data = raw_data[:, force_idx] * force_multiplier * -1 
    
    current_positions = time_steps * omega_m 

    combined_force = np.vstack((force_data, current_positions))
    
    if use_alt_point:
        combined_force = alternetive_first_point(data = combined_force,
                                               remove_last_point = True,
                                               last_row_is_position = True)
    else:
        combined_force = combined_force[:, :-1]

    motor.record.axial_force_fem = combined_force.copy()
    # Tinh trung binh dua tren mang da duoc xu ly khoang nua mo
    motor.record.average_axial_force_fem = np.mean(combined_force[0, :])

    print(f"Native Export: {report_name} processed.")
    return None