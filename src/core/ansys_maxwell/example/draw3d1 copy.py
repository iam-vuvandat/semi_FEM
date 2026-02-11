import os
import time
import glob
from pyaedt import Maxwell3d
import paths 

# =========================
# 1. SETUP
# =========================
os.system("taskkill /F /IM ansysedt.exe /T")
os.system("taskkill /F /IM AnsysGRPC.exe /T")

ansoft_dir = r"C:\Users\Surface\Documents\Ansoft"
for f in glob.glob(os.path.join(ansoft_dir, "*.aedt.auto")):
    try: os.remove(f)
    except: pass
time.sleep(2)

m3d = Maxwell3d(version="2023.1", new_desktop=True, non_graphical=False)

project_root = paths.configure_path()
save_path = os.path.join(project_root, "Ansys_Projects")
if not os.path.exists(save_path):
    os.makedirs(save_path)
project_name = os.path.join(save_path, "Axial_Motor_Final_EqualRadius.aedt")
m3d.save_project(project_name)

time.sleep(2)
m3d.solution_type = "Transient"
m3d.change_material_override(True)

# ============================================================
# 2. ROTOR YOKE (R = 1.0)
# ============================================================
rotor_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, -0.1], radius=1.0, height=0.1)
rotor_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, -0.1], radius=0.5, height=0.1)
m3d.modeler.subtract(blank_list=[rotor_base], tool_list=[rotor_hole], keep_originals=False)
m3d.modeler[rotor_base].material_name = "steel_1008"
m3d.modeler[rotor_base].name = "rotor_yoke"

# ============================================================
# 3. MAGNET (R = 0.9)
# ============================================================
magnet_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=0.9, height=0.1)
magnet_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=0.5, height=0.1)
m3d.modeler.subtract(blank_list=[magnet_base], tool_list=[magnet_hole], keep_originals=False)

knife_1 = m3d.modeler.create_box(origin=[0, 0, 0], sizes=[0.0001, 2, 1])
m3d.modeler.rotate(knife_1, axis="Z", angle=30)
knife_2 = m3d.modeler.create_box(origin=[0, 0, 0], sizes=[0.0001, 2, 1])
m3d.modeler.rotate(knife_2, axis="Z", angle=-30)

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

_, new_pole = m3d.modeler.duplicate_around_axis(assignment=magnet_pole, axis="Z", angle=90, clones=4)
for i in range(len(new_pole)):
    m3d.modeler[new_pole[i]].material_name = "NdFe30_S" if i % 2 == 0 else "NdFe30_N"

# ============================================================
# 4. MOVING BAND (R = 1.02)
# ============================================================
# Mẹo: R_Band (1.02) > R_Rotor (1.0) để bao bọc lưới.
# Chieu cao Z: Bao trum Rotor (-0.12) den giua khe ho (0.125)

moving_band = m3d.modeler.create_cylinder(
    orientation="Z", 
    origin=[0, 0, -0.12], 
    radius=1.02, 
    height=0.245 # Tu -0.12 den 0.125
)
m3d.modeler[moving_band].name = "moving_band"
m3d.modeler[moving_band].material_name = "vacuum"

motion_setup = m3d.assign_rotate_motion(assignment="moving_band", angular_velocity="1500rpm")
motion_setup.props["BandMappingAngle"] = "1deg"

# ============================================================
# 5. STATOR (R = 1.0) - CÙNG BÁN KÍNH ROTOR
# ============================================================
# Z: 0.15 den 0.25
# R_Out = 1.0 (Bang Rotor)
# R_In = 0.5 (Bang Rotor Hole)

stator_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0.15], radius=1.0, height=0.1)
stator_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0.15], radius=0.5, height=0.1)
m3d.modeler.subtract(blank_list=[stator_base], tool_list=[stator_hole], keep_originals=False)

m3d.modeler[stator_base].material_name = "steel_1008"
m3d.modeler[stator_base].name = "stator_yoke"

# ============================================================
# 6. FINALIZE
# ============================================================
rotating_parts = ["rotor_yoke", "magnet_pole"] + new_pole
m3d.eddy_effects_on(rotating_parts, enable_eddy_effects=True)

region = m3d.modeler.create_region(pad_value=30, pad_type="Percentage Offset")
m3d.assign_insulating(assignment=[region])

m3d.save_project()