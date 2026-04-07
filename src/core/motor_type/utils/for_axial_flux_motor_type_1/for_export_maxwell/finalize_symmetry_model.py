def finalize_symmetry_model(m3d, assignment, exclude):
    # 1. CHỈ lấy các vật thể 3D (Solids), loại bỏ các mặt 2D (Sheets)
    all_solids = m3d.modeler.solid_names
    
    # 2. Đảm bảo loại trừ đúng các tên vật thể
    # Nếu exclude chứa đối tượng (Object) thay vì Tên (String), ta lấy .name
    exclude_names = []
    for item in exclude:
        if isinstance(item, str):
            exclude_names.append(item)
        else:
            exclude_names.append(item.name)

    # Thêm chính khối assignment vào danh sách loại trừ để không tự trừ chính nó
    if assignment not in exclude_names:
        exclude_names.append(assignment)

    # 3. Lọc danh sách dao cắt
    solid_parts = [obj for obj in all_solids if obj not in exclude_names]

    # 4. Thực hiện lệnh Subtract nếu có vật thể để trừ
    if solid_parts:
        try:
            m3d.modeler.subtract(
                blank_list=[assignment], 
                tool_list=solid_parts, 
                keep_originals=True
            )
            # Gán vật liệu chân không cho vùng không khí
            m3d.modeler[assignment].material_name = "vacuum"
        except Exception as e:
            print(f"Warning: Subtract failed but moving on. Error: {e}")