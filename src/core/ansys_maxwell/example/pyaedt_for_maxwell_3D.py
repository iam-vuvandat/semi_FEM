import os
import time
import glob
from pyaedt import Maxwell3d
import paths 
import numpy as np
import math 
pi = math.pi

# Collect Gabages
os.system("taskkill /F /IM ansysedt.exe /T")
os.system("taskkill /F /IM AnsysGRPC.exe /T")

ansoft_dir = r"C:\Users\Surface\Documents\Ansoft"
for f in glob.glob(os.path.join(ansoft_dir, "*.aedt.auto")):
    try: os.remove(f)
    except: pass
time.sleep(1)

# Open Maxwell 3D & Save Project
m3d = Maxwell3d(version="2023.1", new_desktop=True, non_graphical=False)

project_root = paths.configure_path()
save_path = os.path.join(project_root, "Ansys_Projects")
if not os.path.exists(save_path):
    os.makedirs(save_path)
project_name = os.path.join(save_path, "pyAEDT_test.aedt")
m3d.save_project(project_name)

time.sleep(1)
m3d.solution_type = "Transient"
m3d.change_material_override(True)

# Draw geometry

# geometry parameter
## Rotor, unit: mm
pole_number          = 10
rotor_lam_dia        = 150 
magnet_arc           = 140 #deg
magnet_embed_depth   = 5 
magnet_depth         = 40 
magnet_segments      = 1
banding_depth        = 0 
shaft_dia            = 0 
shaft_hole_diameter  = 50 
airgap               = 2 
magnet_length        = 4 
rotor_length         = 6 

## Rotor

rotor_outer_radius = rotor_lam_dia / 2 
rotor_inner_radius = shaft_hole_diameter / 2

rotor_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=rotor_outer_radius, height=rotor_length)
rotor_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=rotor_inner_radius, height=rotor_length)
m3d.modeler.subtract(blank_list=[rotor_base], tool_list=[rotor_hole], keep_originals=False)
m3d.modeler[rotor_base].material_name = "steel_1008"
m3d.modeler[rotor_base].name = "rotor_yoke"

## Magnet
magnet_radius = rotor_outer_radius - magnet_embed_depth
magnet_hole   = magnet_radius - magnet_depth

magnet_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, rotor_length], radius=magnet_radius, height=magnet_length)
magnet_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, rotor_length], radius=magnet_hole, height=magnet_length)
m3d.modeler.subtract(blank_list=[magnet_base], tool_list=[magnet_hole], keep_originals=False)

## Knife for split magnet
pole_arc = 360 / pole_number
magnet_arc_mechanical = pole_arc * (magnet_arc/180)
half_magnet_arc_mechanical = magnet_arc_mechanical / 2 

knife_1 = m3d.modeler.create_box(origin=[0, 0, rotor_length], sizes=[magnet_radius, 0.0001, magnet_length])
m3d.modeler.rotate(knife_1, axis="Z", angle=half_magnet_arc_mechanical)
knife_2 = m3d.modeler.create_box(origin=[0, 0, rotor_length], sizes=[magnet_radius, 0.0001, magnet_length])
m3d.modeler.rotate(knife_2, axis="Z", angle=-half_magnet_arc_mechanical)
m3d.modeler.subtract(blank_list=[magnet_base], tool_list=[knife_1, knife_2], keep_originals=False)
magnet_segments = m3d.modeler.separate_bodies(magnet_base)

if magnet_segments[0].volume >= magnet_segments[1].volume:
    m3d.modeler.delete(magnet_segments[0])
    magnet_pole = magnet_segments[1]
else:
    m3d.modeler.delete(magnet_segments[1])
    magnet_pole = magnet_segments[0]

m3d.modeler[magnet_pole].name = "magnet_pole"
mat_n = m3d.materials.add_material("NdFe30_N")
mat_n.set_magnetic_coercivity(-838000, 0, 0, 1)
mat_s = m3d.materials.add_material("NdFe30_S")
mat_s.set_magnetic_coercivity(-838000, 0, 0, -1)
m3d.modeler[magnet_pole].material_name = "NdFe30_N"

arc_pole = 360 / pole_number
_, new_pole = m3d.modeler.duplicate_around_axis(assignment=magnet_pole, axis="Z", angle = arc_pole, clones=pole_number)
for i in range(len(new_pole)):
    m3d.modeler[new_pole[i]].material_name = "NdFe30_S" if i % 2 == 0 else "NdFe30_N"

## Moving band for Rotor

moving_band = m3d.modeler.create_cylinder(
    orientation="Z", 
    origin=[0, 0, - rotor_length], 
    radius= rotor_outer_radius * 1.1, 
    height= 2 * rotor_length + magnet_length + airgap * 0.5
)

m3d.modeler[moving_band].name = "moving_band"
m3d.modeler[moving_band].material_name = "vacuum"
motion_setup = m3d.assign_rotate_motion(assignment="moving_band", angular_velocity="1500rpm")
motion_setup.props["BandMappingAngle"] = "1deg"

rotating_parts = ["rotor_yoke", "magnet_pole"] + new_pole
m3d.eddy_effects_on(rotating_parts, enable_eddy_effects=False)

## Stator

## Stator, unit: mm
slot_number         = 15
stator_lam_dia      = 150 
stator_bore_dia     = 50 
slot_opening        = 5 
wdg_extension_inner = 0
wdg_extension_outer = 0
slot_width          = 7 
slot_depth          = 15 
slot_corner_radius  = 0
tooth_tip_depth     = 2 
tooth_tip_angle     = 30
stator_length       = 25 

offset_z0 = rotor_length + magnet_length + airgap
stator_outer_radius = stator_lam_dia / 2 
stator_inner_radius = stator_bore_dia / 2

### tooth tip 1 
tooth_tip_1_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, offset_z0], radius=stator_outer_radius, height=tooth_tip_depth)
tooth_tip_1_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, offset_z0], radius=stator_inner_radius, height=tooth_tip_depth)
m3d.modeler.subtract(blank_list=[tooth_tip_1_base], tool_list=[tooth_tip_1_hole], keep_originals=False)
m3d.modeler[tooth_tip_1_base].material_name = "steel_1008"

slot_arc = 360 / slot_number
half_slot_opening = slot_opening / 2

knife_1 = m3d.modeler.create_box(origin=[0, -half_slot_opening, offset_z0], sizes=[stator_outer_radius * 1.5, slot_opening, tooth_tip_depth])
m3d.modeler.rotate(knife_1, axis="Z", angle=slot_arc / 2)

knife_2 = m3d.modeler.create_box(origin=[0, -half_slot_opening, offset_z0], sizes=[stator_outer_radius * 1.5, slot_opening, tooth_tip_depth])
m3d.modeler.rotate(knife_2, axis="Z", angle=-slot_arc / 2)

m3d.modeler.subtract(blank_list=[tooth_tip_1_base], tool_list=[knife_1, knife_2], keep_originals=False)
tooth_tip_segments = m3d.modeler.separate_bodies(tooth_tip_1_base)

if tooth_tip_segments[0].volume <= tooth_tip_segments[1].volume:
    m3d.modeler.delete(tooth_tip_segments[1])
    tooth_tip_1 = tooth_tip_segments[0]
else:
    m3d.modeler.delete(tooth_tip_segments[0])
    tooth_tip_1 = tooth_tip_segments[1]

m3d.modeler[tooth_tip_1].name = "tooth_tip_1"

_, new_teeth = m3d.modeler.duplicate_around_axis(
    assignment=tooth_tip_1, 
    axis="Z", 
    angle=slot_arc, 
    clones=slot_number
)

### tooth_tip_2
#### bottom surface
z_bottom_surface = offset_z0 + tooth_tip_depth
r_mid = (stator_inner_radius + stator_outer_radius) / 2
target_point = [r_mid, 0, z_bottom_surface]
bottom_face_id = m3d.modeler.get_faceid_from_position(position=target_point, assignment=tooth_tip_1)
bottom_surface_sheet = m3d.modeler.create_object_from_face(assignment=bottom_face_id)
m3d.modeler[bottom_surface_sheet].name = "bottom_surface_sheet"

#### top_surface
w1 = (1/2) * (slot_width - slot_opening)
h1 = w1 * np.tan(np.radians(tooth_tip_angle))
z_top_surface = z_bottom_surface + h1
C_in = shaft_hole_diameter * pi
C_in_per_slot = C_in / slot_number
C_in_tooth_tip = C_in_per_slot - slot_width
angle_in_tooth_tip = 2 * np.arctan(C_in_tooth_tip  / stator_bore_dia)

C_out = stator_lam_dia * pi
C_out_per_slot = C_out / slot_number
C_out_tooth_tip = C_out_per_slot - slot_width
angle_out_tooth_tip = 2 * np.arctan(C_out_tooth_tip / stator_lam_dia)

# --- 1. Tạo mặt Top ---
p1_in = [stator_bore_dia/2 * np.cos(-angle_in_tooth_tip/2), stator_bore_dia/2 * np.sin(-angle_in_tooth_tip/2), z_top_surface]
p2_in = [stator_bore_dia/2, 0, z_top_surface] 
p3_in = [stator_bore_dia/2 * np.cos(angle_in_tooth_tip/2), stator_bore_dia/2 * np.sin(angle_in_tooth_tip/2), z_top_surface]
arc_in = m3d.modeler.create_polyline(points=[p1_in, p2_in, p3_in], segment_type="Arc")

p1_out = [stator_lam_dia/2 * np.cos(-angle_out_tooth_tip/2), stator_lam_dia/2 * np.sin(-angle_out_tooth_tip/2), z_top_surface]
p2_out = [stator_lam_dia/2, 0, z_top_surface]
p3_out = [stator_lam_dia/2 * np.cos(angle_out_tooth_tip/2), stator_lam_dia/2 * np.sin(angle_out_tooth_tip/2), z_top_surface]
arc_out = m3d.modeler.create_polyline(points=[p1_out, p2_out, p3_out], segment_type="Arc")

# Nối 2 cung thành mặt Top
top_res = m3d.modeler.connect([arc_in, arc_out])
top_surface_sheet = top_res[0] if isinstance(top_res, list) else top_res

# --- 2. Tạo mặt Bottom ---
p1_in_b = [stator_bore_dia/2 * np.cos(-angle_in_tooth_tip/2), stator_bore_dia/2 * np.sin(-angle_in_tooth_tip/2), z_bottom_surface]
p2_in_b = [stator_bore_dia/2, 0, z_bottom_surface]
p3_in_b = [stator_bore_dia/2 * np.cos(angle_in_tooth_tip/2), stator_bore_dia/2 * np.sin(angle_in_tooth_tip/2), z_bottom_surface]
arc_in_b = m3d.modeler.create_polyline(points=[p1_in_b, p2_in_b, p3_in_b], segment_type="Arc")

p1_out_b = [stator_lam_dia/2 * np.cos(-angle_out_tooth_tip/2), stator_lam_dia/2 * np.sin(-angle_out_tooth_tip/2), z_bottom_surface]
p2_out_b = [stator_lam_dia/2, 0, z_bottom_surface]
p3_out_b = [stator_lam_dia/2 * np.cos(angle_out_tooth_tip/2), stator_lam_dia/2 * np.sin(angle_out_tooth_tip/2), z_bottom_surface]
arc_out_b = m3d.modeler.create_polyline(points=[p1_out_b, p2_out_b, p3_out_b], segment_type="Arc")

# Nối 2 cung thành mặt Bottom
bot_res = m3d.modeler.connect([arc_in_b, arc_out_b])
bottom_surface_sheet = bot_res[0] if isinstance(bot_res, list) else bot_res

# --- 3. Tạo khối Loft tooth_tip_2 ---
# Quan trọng: Đổi tên mặt trước khi connect để Maxwell dễ quản lý
m3d.modeler[top_surface_sheet].name = "top_temp"
m3d.modeler[bottom_surface_sheet].name = "bottom_temp"

tip2_res = m3d.modeler.connect(["bottom_temp", "top_temp"])
tooth_tip_2 = tip2_res[0] if isinstance(tip2_res, list) else tip2_res
m3d.modeler[tooth_tip_2].name = "tooth_tip_2"
m3d.modeler.duplicate_around_axis(
    assignment=tooth_tip_2,
    axis="Z",
    angle=360/slot_number,
    clones=slot_number
)
"""

# Outer Region
region = m3d.modeler.create_region(pad_value=30, pad_type="Percentage Offset")
m3d.assign_insulating(assignment=[region])

# Mesh
all_objects = m3d.modeler.object_names
mesh_targets = [
    obj for obj in all_objects 
    if obj != region              
    and "Line" not in obj        
    and "Sheet" not in obj      
]

maximum_element_length = magnet_length
m3d.mesh.assign_length_mesh(
    assignment=mesh_targets,
    maximum_length=f"{maximum_element_length}mm",
    maximum_elements=None,
    name="Global_Core_Mesh"
)

# Setup Analysis
setup_name = "Setup1"

if setup_name in m3d.setup_names:
    m3d.delete_setup(setup_name)

 
setup = m3d.create_setup(name=setup_name, setup_type="Transient")

 
setup.props["StopTime"] = "10ms"
setup.props["TimeStep"] = "2ms"

 
setup.props["SaveFieldsType"] = "Every N Steps"
setup.props["N Steps"] = "1"
setup.props["Steps From"] = "0s"
setup.props["Steps To"] = "10ms"


setup.props["NonlinearSolverResidual"] = "0.005"
setup.props["ScalarPotential"] = "Second Order"
setup.props["SmoothBHCurve"] = False

setup.update()
m3d.save_project()
# Run
m3d.analyze_setup(setup_name)

"""