import os
import numpy as np
import paths

def airgap_flux_density_export(motor, m3d):
    project_root = paths.configure_path()
    temp_dir = os.path.join(project_root, "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    report_name = "Airgap_Flux_Density_Report_FEM"
    csv_path = os.path.join(temp_dir, f"{report_name}.csv")

    if os.path.exists(csv_path):
        os.remove(csv_path)

    oModule = m3d.odesign.GetModule("ReportSetup")
    all_reports = list(oModule.GetAllReportNames())
    if all_reports:
        oModule.DeleteReports(all_reports)

    oModule.CreateReport(report_name, "Fields", "Rectangular Plot", "Setup1 : Transient", 
        [
            "Context:=", "Airgap_Probe_Line",
            "PointCount:=", 50
        ], 
        ["Distance:=", ["All"], "Time:=", ["0.0s"], "fractions:=", ["Nominal"], "halfAxial:=", ["Nominal"], 
         "endRegion:=", ["Nominal"], "delta:=", ["Nominal"], "conds:=", ["Nominal"], 
         "R1:=", ["Nominal"], "Le1:=", ["Nominal"]], 
        ["X Component:=", "Distance", "Y Component:=", ["B_r", "B_t", "B_z"]]
    )
    oModule.ExportToFile(report_name, csv_path.replace("\\", "/"), False)

    with open(csv_path, 'r') as f:
        header = f.readline().strip().split(',')

    distance_idx = 0
    distance_multiplier = 1.0
    
    br_indices = []
    bt_indices = []
    bz_indices = []
    
    br_multipliers = []
    bt_multipliers = []
    bz_multipliers = []
    
    distance_unit_map = {"[mm]": 1.0, "[m]": 1000.0}
    b_unit_map = {"[tesla]": 1.0, "[mtesla]": 1e-3, "[t]": 1.0}

    for i, col in enumerate(header):
        col_clean = col.replace('"', '').lower()
        if "distance" in col_clean:
            distance_idx = i
            for unit, mult in distance_unit_map.items():
                if unit in col_clean:
                    distance_multiplier = mult
                    break
        elif "b_r" in col_clean:
            br_indices.append(i)
            found_unit = False
            for unit, mult in b_unit_map.items():
                if unit in col_clean:
                    br_multipliers.append(mult)
                    found_unit = True
                    break
            if not found_unit:
                br_multipliers.append(1.0)
        elif "b_t" in col_clean:
            bt_indices.append(i)
            found_unit = False
            for unit, mult in b_unit_map.items():
                if unit in col_clean:
                    bt_multipliers.append(mult)
                    found_unit = True
                    break
            if not found_unit:
                bt_multipliers.append(1.0)
        elif "b_z" in col_clean:
            bz_indices.append(i)
            found_unit = False
            for unit, mult in b_unit_map.items():
                if unit in col_clean:
                    bz_multipliers.append(mult)
                    found_unit = True
                    break
            if not found_unit:
                bz_multipliers.append(1.0)

    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    distances = raw_data[:, distance_idx] * distance_multiplier
    
    b_radial = np.array([raw_data[:, idx] * br_multipliers[i] for i, idx in enumerate(br_indices)]).flatten()
    b_tangential = np.array([raw_data[:, idx] * bt_multipliers[i] for i, idx in enumerate(bt_indices)]).flatten()
    b_axial = np.array([raw_data[:, idx] * bz_multipliers[i] for i, idx in enumerate(bz_indices)]).flatten()

    symmetry_factor = motor.mechanical.symmetry_factor
    theta_max = (2 * np.pi) / symmetry_factor
    
    angular_positions = (distances / np.max(distances)) * theta_max
    
    b_magnitude = np.sqrt(b_radial**2 + b_tangential**2 + b_axial**2)

    combined_data = np.vstack((b_radial, b_tangential, b_axial, b_magnitude, angular_positions))
    
    print(f"\033[92mSuccess: Airgap flux density components exported\033[0m")
    return combined_data