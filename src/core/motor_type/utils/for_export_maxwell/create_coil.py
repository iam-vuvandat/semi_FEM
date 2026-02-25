import math

def create_coil(m3d, points, width, current = "2A", conductors_number = 10, shape="3"):
    # 1. Tao duong dan khep kin (tra ve chuoi)
    closed_points = points + [points[0]]
    path_name = m3d.modeler.create_polyline(
        points=closed_points,
        close_surface=False
    )

    # 2. Tinh toan hinh hoc tai trung diem canh dau tien
    p0 = points[0]
    p1 = points[1]
    mid_point = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2]
    v_dir = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
    
    if abs(v_dir[0]) < 1e-9 and abs(v_dir[1]) < 1e-9:
        perp_vec = [0, 1, 0]
    else:
        perp_vec = [-v_dir[1], v_dir[0], 0]

    # 3. Tao LCS (Luu y: cs_obj.name la chuoi)
    cs_obj = m3d.modeler.create_coordinate_system(
        origin=mid_point,
        x_pointing=v_dir,
        y_pointing=perp_vec
    )
    m3d.modeler.set_working_coordinate_system(cs_obj.name)

    # 4. Tao tiet dien (tra ve chuoi)
    if shape == "round":
        rect_name = m3d.modeler.create_circle(
            orientation="YZ",
            origin=[0, 0, 0],
            radius=width/2,
            is_covered=True
        )
        rect_name2 = m3d.modeler.create_circle(
            orientation="YZ",
            origin=[0, 0, 0],
            radius=width/2,
            is_covered=True
        )
    elif shape in ["triangle", "pentagon", "hexagon"] or (isinstance(shape, int) and shape >= 3 and shape != 4):
        # Xu ly cac da giac deu (Regular Polygons)
        sides_map = {"triangle": 3, "pentagon": 5, "hexagon": 6}
        num_sides = sides_map.get(shape, shape)
        
        rect_name = m3d.modeler.create_regular_polygon(
            orientation="YZ",
            origin=[0, 0, 0],
            start_dir=[0, width/2, 0],
            num_sides=num_sides
        )
        rect_name2 = m3d.modeler.create_regular_polygon(
            orientation="YZ",
            origin=[0, 0, 0],
            start_dir=[0, width/2, 0],
            num_sides=num_sides
        )
    else:
        # Truong hop "square", shape=4 hoac bat ky default nao
        rect_name = m3d.modeler.create_rectangle(
            orientation="YZ",
            origin=[0, -width/2, -width/2],
            sizes=[width, width],
            is_covered=True
        )
        rect_name2 = m3d.modeler.create_rectangle(
            orientation="YZ",
            origin=[0, -width/2, -width/2],
            sizes=[width, width],
            is_covered=True
        )

    m3d.modeler.set_working_coordinate_system("Global")
    
    # 5. Sweep along path
    m3d.modeler.sweep_along_path(
        assignment=rect_name, 
        sweep_object=path_name, 
        draft_angle=0, 
        draft_type='Nature', 
        is_check_face_intersection=False, 
        twist_angle=0
    )

    # 6. Gan vat lieu va don dep
    m3d.assign_material(assignment=rect_name, material="copper")
    m3d.modeler.delete(path_name)

    # 7. Gán Coil Terminal (Tra ve doi tuong BoundaryObject)
    coil_terminal_obj = m3d.assign_coil(assignment = rect_name2, conductors_number= conductors_number)

    return rect_name, coil_terminal_obj