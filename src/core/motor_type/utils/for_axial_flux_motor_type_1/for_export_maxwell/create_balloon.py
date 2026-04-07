import numpy as np 
import math
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.apply_symmetry import apply_symmetry

def create_balloon(motor, m3d=None):
    print("")
    print("-- Inside create_balloon")
    use_symmetry = motor.adaptive_mesh_data.use_symmetry_factor
    
    # --- Extract Geometry ---
    rotor = motor.geometry_data.rotor
    rotor_lam_dia         = rotor.rotor_lam_dia  * 1e3 
    magnet_length         = rotor.magnet_length * 1e3
    rotor_length          = rotor.rotor_length * 1e3
    airgap                = rotor.airgap * 1e3

    stator = motor.geometry_data.stator
    stator_lam_dia       = stator.stator_lam_dia * 1e3
    tooth_tip_depth      = stator.tooth_tip_depth * 1e3
    slot_depth           = stator.slot_depth * 1e3
    stator_length        = stator.stator_length * 1e3

    # 1. Tinh sy_h
    sy_h = stator_length - tooth_tip_depth - slot_depth
    
    # 2. Tinh toan cao do Z
    z_start = -rotor_length 
    z_curr = 0 
    z_curr += rotor_length + magnet_length + airgap         
    z_pos_5 = z_curr + tooth_tip_depth 
    z_curr = z_pos_5 + slot_depth + sy_h + rotor_length        
    z_final_mesh = z_curr
    total_height = z_final_mesh - z_start

    # 3. Tinh toan ban kinh Balloon
    stator_outer_radius = stator_lam_dia / 2
    balloon_radius = stator_outer_radius * 1.1

    if not use_symmetry or use_symmetry:
        # --- Chế độ Full Model ---
        region_cyl = m3d.modeler.create_cylinder(
            orientation="Z",
            origin=[0, 0, z_start],
            radius=balloon_radius,
            height=total_height,
            name="Region_Balloon",
            material="vacuum"
        )
        region_faces = m3d.modeler.get_object_faces(region_cyl.name)
        m3d.assign_insulating(assignment=region_faces, insulation="Balloon_Limit")
        print("--End create_balloon (Full Model)")
        return region_cyl

    else:
        # --- Chế độ Symmetry (Sử dụng hàm apply_symmetry) ---
        
        # 1. Lấy danh sách tất cả vật thể hiện có trong Model
        # Chuyển thành list để tránh lỗi iterator khi danh sách thay đổi do bị xóa
        all_objs = list(m3d.modeler.object_names)
        
        for obj_name in all_objs:
            # Tuyệt đối không áp dụng đối xứng lên chính cái khuôn nếu nó đã tồn tại
            if obj_name == 'symmetry_sector':
                continue
            
            # apply_symmetry sẽ tự động:
            # - Tạo 'symmetry_sector' ở lần gọi đầu tiên
            # - Gọt vật thể nếu có phần giao
            # - Xóa vật thể nếu nằm ngoài (res is None)
            apply_symmetry(obj_name, m3d, motor)

        # 2. Cập nhật lại ID hệ thống sau khi đã dọn dẹp sạch sẽ
        m3d.modeler.refresh_all_ids()

        # 3. Gán biên Insulating cho mặt ngoài của khuôn 'symmetry_sector'
        if 'symmetry_sector' in m3d.modeler.object_names:
            region_faces = m3d.modeler.get_object_faces('symmetry_sector')
            print("List of face: ",region_faces)

            # --- DEBUG SECTION START ---
            print("\n" + "="*80)
            print(f"{'Face ID':<10} | {'Area (mm2)':<15} | {'Center (X, Y, Z)':<35} | {'Radius R':<10}")
            print("-" * 80)

            for face_id in region_faces:
                # 1. Lấy diện tích
                area = m3d.modeler.get_face_area(face_id)
                
                # 2. Lấy tọa độ tâm mặt
                center = m3d.modeler.get_face_center(face_id)
                cx, cy, cz = center
                
                # 3. Tính khoảng cách từ tâm đến trục Z (Bán kính R)
                # Giúp xác định mặt Outer (R lớn nhất)
                r_center = math.sqrt(cx**2 + cy**2)
                
                # 4. In kết quả định dạng cột
                center_str = f"({cx:>8.2f}, {cy:>8.2f}, {cz:>8.2f})"
                print(f"{face_id:<10} | {area:<15.4f} | {center_str:<35} | {r_center:<10.2f}")

            print("="*80 + "\n")
            # --- DEBUG SECTION END ---

            m3d.assign_insulating(assignment=region_faces, insulation="Balloon_Limit")
            
            print(f"--- Final Objects after symmetry: {m3d.modeler.object_names}")
            print("--End create_balloon (Symmetry Mode)")
            
            # Trả về đối tượng sector để đồng bộ kết quả trả về của hàm
            return m3d.modeler.objects_by_name['symmetry_sector']
        
        return None