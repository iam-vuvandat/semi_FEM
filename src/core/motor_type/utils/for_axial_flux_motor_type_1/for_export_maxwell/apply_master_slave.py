import numpy as np
import math
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.apply_symmetry import apply_symmetry

def apply_master_slave(m3d, motor):
    if not motor.adaptive_mesh_data.use_symmetry_factor:
        pass

    else:
        # 1. Khởi tạo khuôn symmetry_sector
        symmetry_sector = apply_symmetry(assignment = None, m3d = m3d, motor = motor)
        
        # 2. Lấy danh sách ID các mặt
        region_faces = m3d.modeler.get_object_faces(symmetry_sector.name)
        
        insulating_list = []
        planar_faces_info = []
        master_slave_pair = []

        # 3. Phân loại mặt và xử lý lỗi Non-planar
        for face_id in region_faces:
            area = m3d.modeler.get_face_area(face_id)
            try:
                # Lệnh này sẽ gây lỗi Script macro error nếu là mặt cong
                center = m3d.modeler.get_face_center(face_id)
                if center:
                    planar_faces_info.append({
                        'id': face_id, 
                        'area': area, 
                        'z': center[2],
                        'center': center
                    })
                else:
                    insulating_list.append(face_id)
            except:
                # Nếu không phải mặt phẳng, đưa vào danh sách Insulating
                insulating_list.append(face_id)

        # 4. Gom nhóm mặt phẳng theo Area và Z để tìm Master/Slave
        unique_groups = []
        for f in planar_faces_info:
            found = False
            for group in unique_groups:
                if math.isclose(f['area'], group['area'], rel_tol=1e-3):
                    group['faces'].append(f)
                    found = True
                    break
            if not found:
                unique_groups.append({'area': f['area'], 'faces': [f]})

        for group in unique_groups:
            faces = group['faces']
            if len(faces) == 2:
                z1, z2 = faces[0]['z'], faces[1]['z']
                if not math.isclose(z1, z2, abs_tol=1e-2):
                    insulating_list.append(faces[0]['id'])
                    insulating_list.append(faces[1]['id'])
                else:
                    master_slave_pair = [faces[0]['id'], faces[1]['id']]

        # 5. Gán biên Insulating
        if insulating_list:
            m3d.assign_insulating(assignment=insulating_list, insulation="Balloon_Limit")

        # 6. Gán biên Master/Slave (Sử dụng định dạng string "value+unit")
        if len(master_slave_pair) == 2:
            f_master = master_slave_pair[0]
            f_slave = master_slave_pair[1]
            
            c_m = next(f['center'] for f in planar_faces_info if f['id'] == f_master)
            c_s = next(f['center'] for f in planar_faces_info if f['id'] == f_slave)

            def to_units(coord_list):
                return [f"{val}mm" for val in coord_list]

            m3d.assign_master_slave(
                independent=f_master,
                dependent=f_slave,
                u_vector_origin_coordinates_master=to_units([0, 0, c_m[2]]),
                u_vector_pos_coordinates_master=to_units([c_m[0], c_m[1], c_m[2]]),
                u_vector_origin_coordinates_slave=to_units([0, 0, c_s[2]]),
                u_vector_pos_coordinates_slave=to_units([c_s[0], c_s[1], c_s[2]]),
                reverse_master=False,
                reverse_slave=True,
                same_as_master=True,
                bound_name="Symmetry_Matching"
            )
    return symmetry_sector