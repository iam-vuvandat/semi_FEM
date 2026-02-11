import os
import time
import glob
from pyaedt import Maxwell3d



os.system("taskkill /F /IM ansysedt.exe /T")
os.system("taskkill /F /IM AnsysGRPC.exe /T")
ansoft_dir = r"C:\Users\Surface\Documents\Ansoft"
for f in glob.glob(os.path.join(ansoft_dir, "*.aedt.auto")):
    try: os.remove(f)
    except: pass
time.sleep(2)

# Mở maxwell 3D
m3d = Maxwell3d(version="2023.1", new_desktop=True, non_graphical=False)
time.sleep(5)
m3d.solution_type = "Transient"
time.sleep(5)

# Rotor
moving_band = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, -0.1], radius=1.0, height=0.2)
m3d.modeler[moving_band].name = "moving_band"
# Rotor Yoke 

rotor_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, -0.1], radius=1.0, height=0.1)
rotor_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, -0.1], radius=0.5, height=0.1)
m3d.modeler.subtract(blank_list=[rotor_base], tool_list=[rotor_hole], keep_originals=False)
m3d.modeler[rotor_base].material_name = "steel_1008"
m3d.modeler[rotor_base].name = "rotor_yoke"

# Magnet
magnet_base = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=0.9, height=0.1)
magnet_hole = m3d.modeler.create_cylinder(orientation="Z", origin=[0, 0, 0], radius=0.5, height=0.1)
m3d.modeler.subtract(blank_list=[magnet_base], tool_list=[magnet_hole], keep_originals=False)

## knife for split magnet
knife_1 =  m3d.modeler.create_box(origin=[0, 0, 0], sizes=[0.0001, 2, 1])
m3d.modeler.rotate(knife_1, axis="Z", angle=30)
knife_2 =  m3d.modeler.create_box(origin=[0, 0, 0], sizes=[0.0001, 2, 1])
m3d.modeler.rotate(knife_2, axis="Z", angle=-30)

all_knives = [knife_1,knife_2]
m3d.modeler.subtract(blank_list=[magnet_base], tool_list=all_knives, keep_originals=False)
magnet_segments = m3d.modeler.separate_bodies(magnet_base)
magnet_segments_volume = [0.0, 0.0]

for i in [0,1]:
    magnet_segments_volume[i] = magnet_segments[i].volume

if magnet_segments_volume[0]>=  magnet_segments_volume[1]:
    m3d.modeler.delete(magnet_segments[0])
    magnet_pole = magnet_segments[1]
else:
    m3d.modeler.delete(magnet_segments[1])
    magnet_pole = magnet_segments[0]

m3d.modeler[magnet_pole].name = "magnet_pole"
## Magnet material
mat_n = m3d.materials.add_material("NdFe30_N")
mat_n.relative_permeability = 1.0445730167132
mat_n.conductivity = 625000
mat_n.set_magnetic_coercivity(-838000, 0, 0, 1)

mat_s = m3d.materials.add_material("NdFe30_S")
mat_s.relative_permeability = 1.0445730167132
mat_s.conductivity = 625000
mat_s.set_magnetic_coercivity(-838000, 0, 0, -1)

m3d.modeler[magnet_pole].material_name = "NdFe30_N"

# Nhân bản 
n_time = 4
_,new_pole = m3d.modeler.duplicate_around_axis(
    assignment= magnet_pole,
    axis="Z",
    angle=90,
    clones=4
)

for i in range(len(new_pole)):
    if i % 2 ==0 : 
        m3d.modeler[new_pole[i]].material_name = "NdFe30_S"
    else:
        m3d.modeler[new_pole[i]].material_name = "NdFe30_N"

time.sleep(5)

assignment = moving_band
coordinate_system = "Global"
axis = "Z"
positive_movement = True
start_position = 0
has_rotation_limits = False
angular_velocity = "1500rpm"

motion_setup = m3d.assign_rotate_motion(
    assignment=assignment,
    coordinate_system=coordinate_system,
    axis=axis,
    positive_movement=positive_movement,
    start_position=start_position,
    has_rotation_limits=has_rotation_limits,
    angular_velocity=angular_velocity
)
