def create_balloon(motor, m3d=None):
    # extract geometry
    rotor = motor.geometry_data.rotor
    rotor_lam_dia        = rotor.rotor_lam_dia  * 1e3 
    magnet_length        = rotor.magnet_length * 1e3
    rotor_length         = rotor.rotor_length * 1e3
    airgap               = rotor.airgap * 1e3

    stator = motor.geometry_data.stator
    stator_lam_dia      = stator.stator_lam_dia * 1e3
    slot_width          = stator.slot_width * 1e3
    slot_opening        = stator.slot_opening * 1e3
    tooth_tip_angle     = stator.tooth_tip_angle
    tooth_tip_depth     = stator.tooth_tip_depth * 1e3
    slot_depth          = stator.slot_depth * 1e3
    stator_length       = stator.stator_length * 1e3

    # --- Logic mo phong lai qua trinh cong don cua z_curr ---
    
    # 1. Tinh sy_h (Chieu cao gong stator)
    sy_h = stator_length - tooth_tip_depth - slot_depth
    
    # 2. Mo phong trinh tu z_curr cua create_adaptive_mesh:
    # z_ia bat dau tu -rotor_length va ket thuc tai 0
    z_start = -rotor_length 
    
    z_curr = 0 # Tai diem ket thuc cua z_ia
    z_curr += rotor_length   # sau z_ry
    z_curr += magnet_length  # sau z_mg
    z_curr += airgap         # sau z_ag
    
    z_pos_5 = z_curr + tooth_tip_depth # Diem bat dau cua z_tb (slot)
    
    z_curr = z_pos_5 + slot_depth # sau z_tb
    z_curr += sy_h                # sau z_sy
    z_curr += rotor_length        # sau z_oa (Diem ket thuc cuoi cung)
    
    z_final_mesh = z_curr
    
    # 3. Chieu cao tong cua hinh tru phai bao phu tu z_start den z_final_mesh
    total_height = z_final_mesh - z_start

    # 4. Ban kinh mo rong 1.1 lan ban kinh ngoai Stator
    stator_outer_radius = stator_lam_dia / 2
    balloon_radius = stator_outer_radius * 1.1

    # --- Thuc thi lenh m3d ---
    region_cyl = m3d.modeler.create_cylinder(
        orientation="Z",
        origin=[0, 0, z_start],
        radius=balloon_radius,
        height=total_height,
        name="Region_Balloon",
        material="vacuum"
    )

    # Lay danh sach mat va gan bien Boundary (Theo log truoc do la thanh cong)
    region_faces = m3d.modeler.get_object_faces(region_cyl.name)
    m3d.assign_insulating(assignment=region_faces, insulation="Balloon_Limit")

    return region_cyl