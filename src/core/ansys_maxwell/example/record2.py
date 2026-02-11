import os
import time
from pyaedt import Maxwell2d
import paths

# Init Path
try:
    os.system("taskkill /F /IM ansysedt.exe /T")
    time.sleep(2) 
    os.system("taskkill /F /IM AnsysGRPC.exe /T")
    time.sleep(2)
except:
    time.sleep(2) 

root_path = paths.configure_path()
project_name = "semi_FEM_Solve_Final"
save_path = os.path.join(root_path, "Ansys_Projects", project_name + ".aedt")

if not os.path.exists(os.path.dirname(save_path)):
    os.makedirs(os.path.dirname(save_path))

# --- BƯỚC 2: KHỞI TẠO ---
m2d = Maxwell2d(
    version="2023.1", 
    new_desktop=True, 
    non_graphical=False
)

print("Đang đợi hệ thống ổn định...")
time.sleep(6)

# Đảm bảo làm việc trên Design chuẩn
if "Maxwell2DDesign1" not in m2d.design_list:
    m2d.insert_design("Maxwell2DDesign1")
m2d.set_active_design("Maxwell2DDesign1")

oProject = m2d.oproject
oDesign = m2d.odesign
oEditor = m2d.modeler.oeditor
oDefinitionManager = oProject.GetDefinitionManager()

# --- 1. DỰNG HÌNH ---
def create_rect_stable(name, x, y, w, h):
    m2d.modeler.create_rectangle(
        origin=[x, y, 0],
        sizes=[w, h],
        name=name,
        material="vacuum"
    )

print("Đang dựng hình học...")
create_rect_stable("Rectangle1", -0.07, 0.01, 0.14, -0.02)
create_rect_stable("Rectangle2", -0.07, 0.02, 0.04, -0.01)
create_rect_stable("Rectangle3", 0.07, 0.02, -0.04, -0.01)
create_rect_stable("Rectangle4", -0.1, 0.07, 0.2, -0.13)

# --- 2. VẬT LIỆU (Giữ nguyên logic đã thành công của Đạt) ---
print("Đang đăng ký vật liệu...")
if "NdFe35_Up" not in m2d.materials.material_keys:
    mat_up = m2d.materials.add_material("NdFe35_Up")
    mat_up.permeability = 1.1
    mat_up.conductivity = 625000
    mat_up.magnetic_coercivity = ["-890000", "0", "1", "0"]

if "NdFe35_Down" not in m2d.materials.material_keys:
    mat_down = m2d.materials.add_material("NdFe35_Down")
    mat_down.permeability = 1.1
    mat_down.conductivity = 625000
    mat_down.magnetic_coercivity = ["-890000", "0", "-1", "0"]

m2d.modeler["Rectangle1"].material_name = "steel_1008"
m2d.modeler["Rectangle2"].material_name = "NdFe35_Up"
m2d.modeler["Rectangle3"].material_name = "NdFe35_Down"
m2d.modeler["Rectangle4"].material_name = "vacuum"

# --- 3. BIÊN BALLOON (FIX LỖI GRPC) ---
print("Đang gán biên Balloon...")
rect4_edges = m2d.modeler.get_object_edges("Rectangle4")
if rect4_edges:
    # Sử dụng lệnh Native để tránh lỗi GrpcApiError
    oBoundaryModule = oDesign.GetModule("BoundarySetup")
    oBoundaryModule.AssignBalloon(
        [
            "NAME:Balloon1",
            "Edges:=", rect4_edges,
            "CarbonLowEfficiency:=", False
        ])

# --- 4. THIẾT LẬP GIẢI ---
setup_name = "Setup1"
if setup_name not in m2d.setup_names:
    m2d.create_setup(setupname=setup_name, setup_type="Magnetostatic")

oAnalysisModule = oDesign.GetModule("AnalysisSetup")
oAnalysisModule.EditSetup(setup_name, ["NAME:"+setup_name, "MaximumPasses:=", 10, "PercentError:=", 1])

# --- 5. LƯU VÀ GIẢI ---
m2d.save_project(save_path)
print("Kiểm tra mô hình (Validation)...")
m2d.validate_simple()

print(f"Bắt đầu giải {setup_name}...")
# Lệnh Analyze ổn định nhất cho bản 0.13.0
oDesign.Analyze(setup_name)

# --- 6. TẠO B-MAP ---
print("Đang vẽ biểu đồ mật độ từ thông B...")
oFieldsModule = oDesign.GetModule("FieldsReporter")
all_rects = ["Rectangle1", "Rectangle2", "Rectangle3"]
all_faces = []
for r in all_rects:
    all_faces.extend(m2d.modeler.get_object_faces(r))

if all_faces:
    oFieldsModule.CreateFieldPlot(
        [
            "NAME:Mag_B_Map",
            "SolutionName:=", f"{setup_name} : LastAdaptive",
            "QuantityName:=", "Mag_B",
            "PlotFolder:=", "B",
            "PlotGeomInfo:=", [1, "Surface", "FacesList", len(all_faces)] + [str(f) for f in all_faces]
        ], "Field")

print("-" * 30)
print(f"XONG! Đạt kiểm tra kết quả tại: {save_path}")
print("-" * 30)

input("Nhấn Enter để kết thúc và đi ngủ thôi...")