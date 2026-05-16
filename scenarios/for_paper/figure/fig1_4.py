import vtk
import numpy as np

# ==============================================================================
# CẤU HÌNH THÔNG SỐ (CONFIGURATION)
# ==============================================================================

# 1. Thông số lưới hình học (Mesh Parameters)
BAN_KINH_TRONG = 35
BAN_KINH_NGOAI = 100
GOC_BAT_DAU_DEG = 90 - (100)/2
GOC_KET_THUC_DEG = 90 + (100)/2
CHIEU_CAO_MIN = 0.0
CHIEU_CAO_MAX = 60

# 2. Độ thưa của lưới (Grid Density)
SO_LOP_BAN_KINH = 6
SO_PHAN_DOAN_GOC = 10
SO_LOP_CHIEU_CAO = 2

# 3. Kích thước linh kiện MRN (Component Dimensions)
BAN_KINH_NUT_TRUNG_TAM = 0.2
BAN_KINH_NGUON_MMF = 1.0
BAN_KINH_TU_TRO = 0.5
BAN_KINH_NHANH_DAN = 0.1

# 4. Thông số hiển thị (Visual Settings)
DO_TRONG_SUOT_VOXEL = 0.05
DO_TRONG_SUOT_NGUON_MMF = 1.0  # Đã chỉnh thành 1.0 (Đặc 100%)
DO_PHAN_GIAI_KHOI = 200        # Phân giải siêu nét

# 5. Màu sắc (RGB 0.0 - 1.0)
MAU_VO_VOXEL_BAT_DAU = (0.75, 0.88, 1.0) 
MAU_VO_VOXEL_KET_THUC = (1.0, 1.0, 1.0)  
MAU_NUT_TRUNG_TAM = (0.3, 0.3, 0.3)
MAU_NGUON_MMF = (1.0, 0.0, 0.0)         
MAU_TU_TRO = (0.0, 0.0, 0.0)             
MAU_NHANH_DAN = (0.0, 0.0, 0.0)

# 6. Góc nhìn Camera ban đầu (Initial Camera View)
GOC_AZIMUTH_BAN_DAU = 0.0      # Góc xoay ngang (độ)
GOC_ELEVATION_BAN_DAU = 25.0   # Góc xoay dọc (độ)
MUC_ZOOM_BAN_DAU = 1.2         # Mức phóng to
BUOC_CHINH_GOC = 1.0           # Độ nhạy chỉnh tinh khi bấm phím mũi tên (độ)

# ==============================================================================
# LOGIC XỬ LÝ LƯỚI & LINH KIỆN
# ==============================================================================

R = np.linspace(BAN_KINH_TRONG, BAN_KINH_NGOAI, SO_LOP_BAN_KINH)
Theta = np.linspace(np.radians(GOC_BAT_DAU_DEG), np.radians(GOC_KET_THUC_DEG), SO_PHAN_DOAN_GOC)
Z = np.linspace(CHIEU_CAO_MIN, CHIEU_CAO_MAX, SO_LOP_CHIEU_CAO)

renderer = vtk.vtkRenderer()
renderer.SetBackground(1, 1, 1)
renderer.SetUseFXAA(True)

def create_sphere(center, radius, color, opacity=1.0):
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(center)
    sphere.SetRadius(radius)
    sphere.SetPhiResolution(DO_PHAN_GIAI_KHOI)
    sphere.SetThetaResolution(DO_PHAN_GIAI_KHOI)
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphere.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetOpacity(opacity)
    actor.GetProperty().SetAmbient(0.3)
    actor.GetProperty().SetDiffuse(0.7)
    actor.GetProperty().SetSpecular(0.2)
    return actor

def create_oriented_cylinder(start, end, radius, color, opacity=1.0):
    start, end = np.array(start), np.array(end)
    vec = end - start
    length = np.linalg.norm(vec)
    if length == 0: return None
    
    cylinder = vtk.vtkCylinderSource()
    cylinder.SetRadius(radius)
    cylinder.SetHeight(length)
    cylinder.SetResolution(DO_PHAN_GIAI_KHOI)
    
    mid_point = (start + end) / 2.0
    v = vec / length
    y_axis = np.array([0, 1, 0])
    axis = np.cross(y_axis, v)
    angle = np.degrees(np.arccos(np.clip(np.dot(y_axis, v), -1.0, 1.0)))
    
    transform = vtk.vtkTransform()
    transform.Translate(mid_point)
    if np.linalg.norm(axis) > 1e-6: 
        transform.RotateWXYZ(angle, axis)
        
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetTransform(transform)
    transform_filter.SetInputConnection(cylinder.GetOutputPort())
    
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(transform_filter.GetOutputPort())
    
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetOpacity(opacity)
    actor.GetProperty().SetAmbient(0.3)
    actor.GetProperty().SetDiffuse(0.7)
    return actor

for i in range(len(R) - 1):
    t_color = i / (len(R) - 2) if len(R) > 2 else 0
    current_color = np.array(MAU_VO_VOXEL_BAT_DAU) + (np.array(MAU_VO_VOXEL_KET_THUC) - np.array(MAU_VO_VOXEL_BAT_DAU)) * t_color
    
    for j in range(len(Theta) - 1):
        for k in range(len(Z) - 1):
            r_v, t_v, z_v = [R[i], R[i+1]], [Theta[j], Theta[j+1]], [Z[k], Z[k+1]]
            pts = np.array([
                [r_v[0]*np.cos(t_v[0]), r_v[0]*np.sin(t_v[0]), z_v[0]],
                [r_v[0]*np.cos(t_v[1]), r_v[0]*np.sin(t_v[1]), z_v[0]],
                [r_v[1]*np.cos(t_v[1]), r_v[1]*np.sin(t_v[1]), z_v[0]],
                [r_v[1]*np.cos(t_v[0]), r_v[1]*np.sin(t_v[0]), z_v[0]],
                [r_v[0]*np.cos(t_v[0]), r_v[0]*np.sin(t_v[0]), z_v[1]],
                [r_v[0]*np.cos(t_v[1]), r_v[0]*np.sin(t_v[1]), z_v[1]],
                [r_v[1]*np.cos(t_v[1]), r_v[1]*np.sin(t_v[1]), z_v[1]],
                [r_v[1]*np.cos(t_v[0]), r_v[1]*np.sin(t_v[0]), z_v[1]]
            ])
            
            points = vtk.vtkPoints()
            for p in pts: points.InsertNextPoint(p)
            hex_cell = vtk.vtkHexahedron()
            for idx in range(8): hex_cell.GetPointIds().SetId(idx, idx)
            grid = vtk.vtkUnstructuredGrid()
            grid.SetPoints(points)
            grid.InsertNextCell(hex_cell.GetCellType(), hex_cell.GetPointIds())
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputData(grid)
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(current_color)
            actor.GetProperty().SetOpacity(DO_TRONG_SUOT_VOXEL)
            actor.GetProperty().SetEdgeVisibility(True)
            actor.GetProperty().SetEdgeColor(0, 0, 0)
            actor.GetProperty().SetLineWidth(0.8)
            renderer.AddActor(actor)

            center_node = np.mean(pts, axis=0)
            face_centers = [
                np.mean(pts[[0,1,5,4]], axis=0), np.mean(pts[[2,3,7,6]], axis=0), 
                np.mean(pts[[0,3,7,4]], axis=0), np.mean(pts[[1,2,6,5]], axis=0), 
                np.mean(pts[[0,1,2,3]], axis=0), np.mean(pts[[4,5,6,7]], axis=0)  
            ]
            renderer.AddActor(create_sphere(center_node, BAN_KINH_NUT_TRUNG_TAM, MAU_NUT_TRUNG_TAM))

            for f_idx, f_center in enumerate(face_centers):
                # Loại bỏ nhánh ở các biên
                if i == 0 and f_idx == 0: continue
                if i == len(R) - 2 and f_idx == 1: continue
                if k == 0 and f_idx == 4: continue
                if k == len(Z) - 2 and f_idx == 5: continue

                vec_full = f_center - center_node
                L = np.linalg.norm(vec_full)
                u = vec_full / L
                
                p_rel_start = center_node + u * (L * 0.15)
                p_rel_end   = center_node + u * (L * 0.45)
                p_mmf_center = center_node + u * (L * 0.80)
                
                renderer.AddActor(create_oriented_cylinder(p_rel_start, p_rel_end, BAN_KINH_TU_TRO, MAU_TU_TRO))
                renderer.AddActor(create_sphere(p_mmf_center, BAN_KINH_NGUON_MMF, MAU_NGUON_MMF, opacity=DO_TRONG_SUOT_NGUON_MMF))
                renderer.AddActor(create_oriented_cylinder(center_node + u*BAN_KINH_NUT_TRUNG_TAM, p_rel_start, BAN_KINH_NHANH_DAN, MAU_NHANH_DAN))
                renderer.AddActor(create_oriented_cylinder(p_rel_end, p_mmf_center - u*BAN_KINH_NGUON_MMF, BAN_KINH_NHANH_DAN, MAU_NHANH_DAN))
                renderer.AddActor(create_oriented_cylinder(p_mmf_center + u*BAN_KINH_NGUON_MMF, f_center, BAN_KINH_NHANH_DAN, MAU_NHANH_DAN))

# ==============================================================================
# RENDER & CAMERA CONTROLS
# ==============================================================================

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(2000, 2000)
render_window.SetWindowName("Publication Quality MRN Grid - VTK")
render_window.SetMultiSamples(16) # Khử răng cưa cực mạnh

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

camera = renderer.GetActiveCamera()
renderer.ResetCamera()

# Áp dụng góc nhìn ban đầu từ phần cấu hình
camera.Azimuth(GOC_AZIMUTH_BAN_DAU)
camera.Elevation(GOC_ELEVATION_BAN_DAU)
camera.Zoom(MUC_ZOOM_BAN_DAU)

# Actor hiển thị tọa độ camera
text_actor = vtk.vtkTextActor()
text_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
text_actor.SetPosition(0.01, 0.88)
text_property = text_actor.GetTextProperty()
text_property.SetFontSize(16)
text_property.SetColor(0.0, 0.0, 0.0)
text_property.SetBackgroundColor(1.0, 1.0, 1.0)
text_property.SetBackgroundOpacity(0.7)
renderer.AddActor2D(text_actor)

def update_camera_info(obj=None, event=None):
    pos = camera.GetPosition()
    focal = camera.GetFocalPoint()
    up = camera.GetViewUp()
    info = (f"[CHỈNH TINH BẰNG PHÍM MŨI TÊN]\n\n"
            f"Camera Position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})\n"
            f"Focal Point:     ({focal[0]:.2f}, {focal[1]:.2f}, {focal[2]:.2f})\n"
            f"View Up:         ({up[0]:.2f}, {up[1]:.2f}, {up[2]:.2f})\n\n"
            f"* Copy các tọa độ này vào config\n"
            f"  nếu muốn thiết lập lại góc nhìn này.")
    text_actor.SetInput(info)
    render_window.Render()

# Bắt sự kiện phím mũi tên để chỉnh tinh (Fine-tune)
def on_key_press(obj, event):
    key = obj.GetKeySym()
    
    if key == "Up":
        camera.Elevation(BUOC_CHINH_GOC)
    elif key == "Down":
        camera.Elevation(-BUOC_CHINH_GOC)
    elif key == "Left":
        camera.Azimuth(BUOC_CHINH_GOC)
    elif key == "Right":
        camera.Azimuth(-BUOC_CHINH_GOC)
    else:
        return # Bỏ qua các phím khác
    
    camera.OrthogonalizeViewUp() # Giữ camera không bị lật nghiêng (roll)
    update_camera_info()

interactor.AddObserver('KeyPressEvent', on_key_press)
interactor.AddObserver('EndInteractionEvent', update_camera_info)

update_camera_info()
render_window.Render()
interactor.Start()