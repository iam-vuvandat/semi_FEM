import paths
import numpy as np
import os
from src.core.solver.utils.convert_to_dq import convert_to_dq
from src.core.solver.utils.periodic_derivative import periodic_derivative
from src.core.solver.utils.calculate_line_to_line_back_emf import calculate_line_to_line_back_emf
from src.core.solver.utils.alternetive_first_point import alternetive_first_point



def flux_linkage_export(motor, m3d):
    project_root = paths.configure_path()
    n_phase = motor.winding_data.phase
    poles = motor.geometry_data.rotor.pole_number
    
    omega_m = motor.mechanical.omega

    temp_dir = os.path.join(project_root, "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    phase_map = ["A", "B", "C", "D", "E", "F"]
    y_expressions = [f"FluxLinkage(Phase{phase_map[i]})" for i in range(n_phase)]
    
    report_name = "Flux_Linkage_Report_FEM"
    csv_path = os.path.join(temp_dir, f"{report_name}.csv")

    if os.path.exists(csv_path):
        os.remove(csv_path)

    oModule = m3d.odesign.GetModule("ReportSetup")
    all_reports = list(oModule.GetAllReportNames())
    if all_reports:
        oModule.DeleteReports(all_reports)

    oModule.CreateReport(report_name, "Transient", "Rectangular Plot", "Setup1 : Transient", 
        ["Domain:=", "Sweep"], 
        ["Time:=", ["All"], "fractions:=", ["Nominal"], "halfAxial:=", ["Nominal"], 
         "endRegion:=", ["Nominal"], "delta:=", ["Nominal"], "conds:=", ["Nominal"], 
         "R1:=", ["Nominal"], "Le1:=", ["Nominal"]], 
        ["X Component:=", "Time", "Y Component:=", y_expressions]
    )
    oModule.ExportToFile(report_name, csv_path.replace("\\", "/"), False)

    with open(csv_path, 'r') as f:
        header = f.readline().strip().split(',')

    time_idx = 0
    time_multiplier = 1.0
    flux_indices = []
    flux_multipliers = []
    
    time_unit_map = {"[s]": 1.0, "[ms]": 1e-3, "[us]": 1e-6}
    flux_unit_map = {"[wb]": 1.0, "[mwb]": 1e-3}

    for i, col in enumerate(header):
        col_clean = col.replace('"', '').lower()
        
        if "time" in col_clean:
            time_idx = i
            for unit, mult in time_unit_map.items():
                if unit in col_clean:
                    time_multiplier = mult
                    break
        elif "fluxlinkage" in col_clean:
            flux_indices.append(i)
            found_unit = False
            for unit, mult in flux_unit_map.items():
                if unit in col_clean:
                    flux_multipliers.append(mult)
                    found_unit = True
                    break
            if not found_unit:
                flux_multipliers.append(1.0)

    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    time_steps = raw_data[:, time_idx] * time_multiplier
    flux_phases_list = []
    for i, idx in enumerate(flux_indices):
        flux_phases_list.append(raw_data[:, idx] * flux_multipliers[i])
    flux_phases = np.array(flux_phases_list)

    # THỰC HIỆN OFFSET HÀNG: pha A -> pha B, pha B -> pha C, ...
    # Dùng np.roll với shift=1 trên trục 0 (trục chứa các pha)
    flux_phases = np.roll(flux_phases, shift=1, axis=0)
    
    n_steps = len(time_steps)
    
    # Xác định offset và tính toán chuẩn góc duy nhất
    offset = motor.geometry_data.geometry_option.rotor_mechanical_synchronized
    current_positions = (time_steps * omega_m) + offset

    d_axis_flux = np.empty(n_steps)
    q_axis_flux = np.empty(n_steps)

    for i in range(n_steps):
        pos = current_positions[i]
        temp_val = np.empty((n_phase + 1, 1))
        temp_val[:-1, 0] = flux_phases[:, i]
        temp_val[-1, 0] = pos
        
        # Biến đổi DQ dựa trên dữ liệu pha đã được offset
        dq_data = convert_to_dq(temp_val, poles, pos)
        d_axis_flux[i] = dq_data[0, 0]
        q_axis_flux[i] = dq_data[1, 0]

    # Lưu trữ dữ liệu với hàng cuối cùng là current_positions đã offset
    combined_data = np.vstack((d_axis_flux, q_axis_flux, flux_phases, current_positions))

    # Tính toán Back-EMF từ dữ liệu pha đã offset
    back_emf = periodic_derivative(data=combined_data[2:], half_open_interval=True).derivative * omega_m
    
    motor.record.flux_linkage_fem = combined_data.copy()
    motor.record.back_emf_fem = back_emf.copy()
    
    print(f"\033[92mSuccess: Flux Linkage exported, shifted (A->B, B->C) and synchronized (Offset: {offset:.4f} rad)\033[0m")