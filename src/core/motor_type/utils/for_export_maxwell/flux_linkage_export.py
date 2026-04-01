import paths
import numpy as np
import os
from src.core.solver.utils.convert_to_dq import convert_to_dq
from src.core.solver.utils.periodic_derivative import periodic_derivative
from src.core.solver.utils.calculate_line_to_line_back_emf import calculate_line_to_line_back_emf


def flux_linkage_export(motor, m3d):
    project_root = paths.configure_path()
    n_phase = motor.winding_data.phase
    poles = motor.geometry_data.rotor.pole_number
    speed_rpm = getattr(motor.mechanical, 'shaft_speed', 3000)
    omega_m = (speed_rpm * 2 * np.pi) / 60 

    temp_dir = os.path.join(project_root, "data", "temp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    expressions = [f"FluxLinkage(phase{i+1})" for i in range(n_phase)]
    report_name = "Flux_Linkage_Report_FEM"
    csv_path = os.path.join(temp_dir, f"{report_name}.csv")

    # 1. Tạo báo cáo và xuất CSV
    m3d.post.create_report(
        expressions=expressions,
        setup_sweep_name="Setup1 : Transient",
        plot_name=report_name,
        plot_type="Rectangular Plot"
    )
    m3d.post.export_report_to_csv(temp_dir, report_name)

    # 2. Tự động đọc Header để lấy Index và Hệ số đơn vị
    with open(csv_path, 'r') as f:
        header = f.readline().strip().split(',')

    time_idx = -1
    time_multiplier = 1.0
    flux_indices = []
    flux_multipliers = []

    # Map đơn vị thời gian
    time_unit_map = {"[s]": 1.0, "[ms]": 1e-3, "[us]": 1e-6, "[ns]": 1e-9}
    # Map đơn vị từ thông
    flux_unit_map = {"[wb]": 1.0, "[mwb]": 1e-3, "[vs]": 1.0}

    for i, col in enumerate(header):
        col_clean = col.lower()
        
        # Tìm cột thời gian
        if "time" in col_clean:
            time_idx = i
            for unit, mult in time_unit_map.items():
                if unit in col_clean:
                    time_multiplier = mult
                    break
        
        # Tìm cột từ thông các pha (chỉ lấy đủ số pha của motor)
        elif "fluxlinkage" in col_clean and len(flux_indices) < n_phase:
            flux_indices.append(i)
            found_unit = False
            for unit, mult in flux_unit_map.items():
                if unit in col_clean:
                    flux_multipliers.append(mult)
                    found_unit = True
                    break
            if not found_unit:
                flux_multipliers.append(1.0) # Mặc định là Wb

    # 3. Đọc dữ liệu số và áp dụng quy đổi đơn vị
    raw_data = np.genfromtxt(csv_path, delimiter=',', skip_header=1)
    
    # Lấy thời gian và đổi sang giây (s)
    time_steps = raw_data[:, time_idx] * time_multiplier
    
    # Lấy từ thông các pha và đổi sang Weber (Wb)
    flux_list = []
    for i, idx in enumerate(flux_indices):
        flux_list.append(raw_data[:, idx] * flux_multipliers[i])
    flux_phases = np.array(flux_list)
    
    n_steps = len(time_steps)
    current_positions = time_steps * omega_m 

    # 4. Biến đổi DQ
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

    # 5. Đóng gói vào record
    combined_data = np.vstack((
        d_axis_flux,        
        q_axis_flux,        
        flux_phases,        
        current_positions   
    ))
    combined_data = combined_data[:,:-1]

    

    # back emf 
    back_emf = periodic_derivative(data=combined_data[2:], half_open_interval=True).derivative * omega_m

    back_emf_line = calculate_line_to_line_back_emf(data_numpy=back_emf)

    # Save to record
    motor.record.flux_linkage_fem = combined_data.copy()
    motor.record.back_emf_fem = back_emf.copy()
    motor.record.back_emf_line_fem = back_emf_line.copy()
