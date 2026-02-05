import json
import os
import ansys.aedt.core

# 1. Cấu hình hệ thống - Giữ nguyên tên biến của hãng
AEDT_VERSION = "2023.1"  # Đã chỉnh về bản của Đạt
NG_MODE = False

# Tránh dùng tempfile để không bị lỗi PermissionError khi giữ Maxwell mở
project_dir = r"C:\Users\Surface\semi_FEM\Ansys_Projects"
if not os.path.exists(project_dir):
    os.makedirs(project_dir)

project_name = os.path.join(project_dir, "choke_fixed.aedt")

# 2. Khởi tạo Maxwell 3D
m3d = ansys.aedt.core.Maxwell3d(
    project=project_name,
    solution_type="EddyCurrent",
    version=AEDT_VERSION,
    non_graphical=NG_MODE,
    new_desktop=True,
)

# 3. Model Preparation - Giữ nguyên 100% cấu trúc hãng
choke_descriptor = {
    "Number of Windings": {"1": False, "2": False, "3": True, "4": False},
    "Layer": {"Simple": False, "Double": False, "Triple": True},
    "Layer Type": {"Separate": False, "Linked": True},
    "Similar Layer": {"Similar": False, "Different": True},
    "Mode": {"Differential": True, "Common": False},
    "Wire Section": {"None": False, "Hexagon": False, "Octagon": True, "Circle": False},
    "Core": {
        "Name": "Core",
        "Material": "ferrite",
        "Inner Radius": 100,
        "Outer Radius": 143,
        "Height": 25,
        "Chamfer": 0.8,
    },
    "Outer Winding": {
        "Name": "Winding",
        "Material": "copper",
        "Inner Radius": 100,
        "Outer Radius": 143,
        "Height": 25,
        "Wire Diameter": 5,
        "Turns": 2,
        "Coil Pit(deg)": 4,
        "Occupation(%)": 0,
    },
    "Mid Winding": {"Turns": 7, "Coil Pit(deg)": 4, "Occupation(%)": 0},
    "Inner Winding": {"Turns": 10, "Coil Pit(deg)": 4, "Occupation(%)": 0},
}

choke_fn = os.path.join(project_dir, "choke_params.json")
with open(choke_fn, "w") as outfile:
    json.dump(choke_descriptor, outfile)

# 4. Create Choke
m3d.modeler.check_choke_values(input_dir=choke_fn, create_another_file=False)
list_object = m3d.modeler.create_choke(input_file=choke_fn)

core = list_object[1]
# Truy cập danh sách cuộn dây từ list_object của hãng
winding_groups = [list_object[2], list_object[3], list_object[4]]

# 5. Assign Excitations & Matrix
matrix_currents = []
for i, group in enumerate(winding_groups):
    w_name = group[0].name
    faces = m3d.modeler.get_object_faces(w_name)
    phase = f"{i*120}deg"
    
    in_name = f"phase_{i+1}_in"
    m3d.assign_current(assignment=[faces[-1]], amplitude=1000, phase=phase, name=in_name)
    m3d.assign_current(assignment=[faces[-2]], amplitude=1000, phase=phase, swap_direction=True, name=f"phase_{i+1}_out")
    matrix_currents.append(in_name)

m3d.assign_matrix(assignment=matrix_currents, matrix_name="current_matrix")

# 6. Mesh & Region (Tăng kích thước Region để đảm bảo hội tụ)
m3d.modeler.create_air_region(200, 200, 200, 200, 200, 200)

# 7. Setup & Analyze
setup_name = "MySetup"
if setup_name not in m3d.setup_names:
    setup = m3d.create_setup(setup_name)
    setup.props["Frequency"] = "100kHz"
    setup.props["MaximumPasses"] = 6  # Giảm passes cho Surface
    setup.update()

m3d.save_project()

# Kiểm tra và chạy giải
print("--- [!] DANG KIEM TRA VA GIAI BAI TOAN... ---")
if m3d.analyze_setup(setup_name):
    print("--- [!] TAO BIEU DO TRUONG B... ---")
    plot_b = m3d.post.create_fieldplot_surface(
        assignment=m3d.modeler.get_object_faces(core.name),
        quantity="Mag_B",
        plot_name="Flux_Density_B"
    )
    m3d.modeler.fit_all()
else:
    print("--- [!] LOI: KHONG THE GIAI BAI TOAN. HAY KIEM TRA MESSAGE MANAGER TRONG MAXWELL ---")

# 8. Finish - Giữ Maxwell mở
m3d.save_project()
# m3d.release_desktop()  # Đã tắt theo yêu cầu của Đạt
print(f"Hoan tat. Project: {project_name}")