import math

def create_conductor(m3d,
                     point_list = None,
                     width = 0,
                     create_terminal = False):
    path_name = m3d.modeler.create_polyline(
        points=point_list,
        close_surface=False
    )

    p0 = point_list[0]
    p1 = point_list[1]
    mid_point = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2]
    v_dir = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
    
    if abs(v_dir[0]) < 1e-9 and abs(v_dir[1]) < 1e-9:
        perp_vec = [0, 1, 0]
    else:
        perp_vec = [-v_dir[1], v_dir[0], 0]

    cs_obj = m3d.modeler.create_coordinate_system(
        origin=mid_point,
        x_pointing=v_dir,
        y_pointing=perp_vec
    )
    m3d.modeler.set_working_coordinate_system(cs_obj.name)

    rect_for_sweep = m3d.modeler.create_rectangle(
        orientation="YZ",
        origin=[0, -width/2, -width/2],
        sizes=[width, width],
        is_covered=True
    )

    rect_to_return = None
    if create_terminal:
        rect_to_return = m3d.modeler.create_rectangle(
            orientation="YZ",
            origin=[0, -width/2, -width/2],
            sizes=[width, width],
            is_covered=True
        )

    m3d.modeler.set_working_coordinate_system("Global")
    
    m3d.modeler.sweep_along_path(
        assignment=rect_for_sweep, 
        sweep_object=path_name, 
        draft_angle=0, 
        draft_type='Nature', 
        is_check_face_intersection=False, 
        twist_angle=0
    )

    m3d.assign_material(assignment=rect_for_sweep, material="copper")
    m3d.modeler.delete(path_name)

    return rect_for_sweep, rect_to_return