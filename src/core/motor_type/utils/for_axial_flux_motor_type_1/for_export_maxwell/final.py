def finalize_symmetry_model(m3d,excule):
    all_objects = m3d.modeler.object_names
    solid_parts = [obj for obj in all_objects if obj not in ["symmetry_sector", "moving_band", "Region"]]
    
    # 2. Lệnh then chốt: Đục rỗng symmetry_sector tại những chỗ có vật thể đặc
    # keep_originals=True là BẮT BUỘC để không làm mất Stator/Rotor của Đạt
    m3d.modeler.subtract(
        blank_list=["symmetry_sector"], 
        tool_list=solid_parts, 
        keep_originals=True
    )
    
