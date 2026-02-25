import paths
import numpy as np
import math 
pi = math.pi

from src.core.motor_type.utils.for_export_maxwell.init_window import init_window
from src.core.motor_type.utils.for_export_maxwell.init_project import init_project
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_balloon import create_balloon

def create_coil(m3d, points, width, current_function, coil_name, fillet=False):
    p0 = points[0]
    p1 = points[1]
    
    mid_point = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2]
    tangent_vec = [p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]]
    
    if tangent_vec[0] == 0 and tangent_vec[1] == 0:
        perp_vec = [1, 0, 0]
    else:
        perp_vec = [-tangent_vec[1], tangent_vec[0], 0]

    reordered_path = [mid_point] + points[1:] + [points[0]]
    
    path_name = f"{coil_name}_Path"
    if path_name in m3d.modeler.object_names:
        m3d.modeler.delete(path_name)
        
    m3d.modeler.create_polyline(
        points=reordered_path, 
        name=path_name, 
        close_surface=True
    )

    cs_name = f"{coil_name}_LCS"
    m3d.modeler.create_coordinate_system(
        origin=mid_point,
        x_pointing=tangent_vec,
        y_pointing=perp_vec,
        name=cs_name,
        reference_cs="Global"
    )
    
    m3d.modeler.set_working_coordinate_system(cs_name)

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

    m3d.modeler.sweep_along_path(assignment=section_sweep, sweep_object=path_name)
    m3d.modeler[section_sweep].name = coil_name
    m3d.assign_material(assignment=coil_name, material="copper")
    
    m3d.assign_current(
        assignment=[section_terminal], 
        amplitude=current_function, 
        name=f"Exc_{coil_name}"
    )

    if fillet:
        # Tu dong tinh ban kinh fillet = 1/4 chieu rong
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

# --- Script test 40 ngoi sao ---
init_window()
m3d = init_project(project_name="Test_Star_40x_AutoFillet", solution_type="Magnetostatic")

r_outer = 50.0  
r_inner = 20.0  
num_points = 5
width_square = 4.0 # Voi width=4.0, fillet_radius se tu dong la 1.0mm
current_val = "10A" 
z_pitch = 15.0 

raw_verts = []
for i in range(num_points * 2):
    angle = i * pi / num_points 
    r = r_outer if i % 2 == 0 else r_inner
    raw_verts.append([r * math.cos(angle), r * math.sin(angle), 0])

coil_base_name = "Copper_Star"
create_coil(
    m3d=m3d, 
    points=raw_verts, 
    width=width_square, 
    current_function=current_val, 
    coil_name=coil_base_name,
    fillet=True
)

m3d.modeler.duplicate_along_line(
    assignment=coil_base_name,
    vector=[0, 0, z_pitch],
    clones=40,
    attach=False
)

create_balloon(pad_value=30, m3d=m3d) 
all_stars = m3d.modeler.get_objects_w_string("Copper_Star")
m3d.mesh.assign_length_mesh(assignment=all_stars, maximum_length="2mm", name="AutoFillet_Mesh")

