import math

def create_coil(m3d, points, width, current_function, coil_name, fillet=True):
    # 1. Tinh toan hinh hoc tai trung diem canh dau tien
    p0 = points[0]
    p1 = points[1]
    
    mid_point = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2]
    tangent_vec = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
    
    # Xac dinh vector vuong goc de tao he toa do LCS
    if tangent_vec[0] == 0 and tangent_vec[1] == 0:
        perp_vec = [1, 0, 0]
    else:
        perp_vec = [-tangent_vec[1], tangent_vec[0], 0]

    # Sap xep lai lo trinh bat dau tu trung diem
    reordered_path = [mid_point] + points[1:] + [points[0]]
    
    path_name = f"{coil_name}_Path"
    if path_name in m3d.modeler.object_names:
        m3d.modeler.delete(path_name)
        
    m3d.modeler.create_polyline(
        points=reordered_path, 
        name=path_name, 
        close_surface=True
    )

    # 2. Tao He toa do cuc bo (LCS)
    cs_name = f"{coil_name}_LCS"
    m3d.modeler.create_coordinate_system(
        origin=mid_point,
        x_pointing=tangent_vec,
        y_pointing=perp_vec,
        name=cs_name,
        reference_cs="Global"
    )
    
    m3d.modeler.set_working_coordinate_system(cs_name)

    # 3. Tao tiet dien VUONG (Sweep va Terminal)
    section_sweep = f"Sec_{coil_name}_Sweep"
    section_terminal = f"Sec_{coil_name}_Term"
    rect_origin = [0, -width/2, -width/2]
    
    m3d.modeler.create_rectangle(
        orientation="YZ",
        origin=rect_origin,
        sizes=[width, width],
        name=section_sweep,
        is_covered=True
    )
    
    m3d.modeler.create_rectangle(
        orientation="YZ",
        origin=rect_origin,
        sizes=[width, width],
        name=section_terminal,
        is_covered=True
    )

    m3d.modeler.set_working_coordinate_system("Global")

    # 4. Sweep va Gan kich tu
    m3d.modeler.sweep_along_path(assignment=section_sweep, sweep_object=path_name)
    m3d.modeler[section_sweep].name = coil_name
    m3d.assign_material(assignment=coil_name, material="copper")
    
    m3d.assign_current(
        assignment=[section_terminal], 
        amplitude=current_function, 
        name=f"Exc_{coil_name}"
    )

    # 5. Boc logic Fillet loi (oEditor)
    if fillet:
        # Tu dong tinh ban kinh fillet = 1/4 width
        auto_radius = f"{width / 4.0}mm"
        edge_ids = m3d.modeler.get_object_edges(coil_name)
        
        m3d.modeler.oeditor.Fillet(
            [
                "NAME:Selections",
                "Selections:="      , coil_name,
                "NewPartsModelFlag:="   , "Model"
            ], 
            [
                "NAME:Parameters",
                [
                    "NAME:FilletParameters",
                    "Edges:="       , edge_ids,
                    "Vertices:="        , [],
                    "Radius:="      , auto_radius,
                    "Setback:="     , "0mm"
                ]
            ])
    
    return coil_name