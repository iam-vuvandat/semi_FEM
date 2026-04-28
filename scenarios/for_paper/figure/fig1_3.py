import vtk
import numpy as np

# ==============================================================================
# CẤU HÌNH THÔNG SỐ (CONFIGURATION)
# ==============================================================================

BAN_KINH_TRONG = 85.0
BAN_KINH_NGOAI = 95.0
GOC_BAT_DAU_DEG = 0.0
GOC_KET_THUC_DEG = 10.0
CHIEU_CAO_MIN = 10.0
CHIEU_CAO_MAX = 20.0

show_r0 = False
show_r1 = True
show_theta0 = True
show_theta1 = True
show_z0 = False
show_z1 = True

BAN_KINH_NUT_TRUNG_TAM = 0.2
BAN_KINH_NGUON_MMF = 0.5
BAN_KINH_TU_TRO = 0.25
BAN_KINH_NHANH_DAN = 0.05

DO_TRONG_SUOT_VOXEL = 0.1
DO_TRONG_SUOT_NGUON_MMF = 0.35  
DO_PHAN_GIAI_KHOI = 200        

MAU_VO_VOXEL = (0.75, 0.88, 1.0) 
MAU_NUT_TRUNG_TAM = (0.3, 0.3, 0.3)
MAU_NGUON_MMF = (1.0, 0.0, 0.0)         
MAU_TU_TRO = (0.0, 0.0, 0.0)             
MAU_NHANH_DAN = (0.0, 0.0, 0.0)
MAU_MUI_TEN = (1.0, 1.0, 1.0) 

# Tọa độ Camera mặc định từ hình ảnh
CAM_POS_X = 106.69
CAM_POS_Y = 35.47
CAM_POS_Z = -38.69
MUC_ZOOM_BAN_DAU = 1.2         
BUOC_CHINH_GOC = 1.0           

# ==============================================================================
# LOGIC XỬ LÝ LƯỚI & LINH KIỆN
# ==============================================================================

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

def create_arrow(center, direction, length, color):
    arrow = vtk.vtkArrowSource()
    arrow.SetShaftRadius(0.1) 
    arrow.SetTipRadius(0.2)   
    arrow.SetTipLength(0.35)
    arrow.SetShaftResolution(DO_PHAN_GIAI_KHOI)
    arrow.SetTipResolution(DO_PHAN_GIAI_KHOI)
    direction = np.array(direction)
    direction = direction / np.linalg.norm(direction)
    x_axis = np.array([1.0, 0.0, 0.0])
    axis = np.cross(x_axis, direction)
    dot = np.dot(x_axis, direction)
    angle = np.degrees(np.arccos(np.clip(dot, -1.0, 1.0)))
    transform = vtk.vtkTransform()
    transform.Translate(center)
    if np.linalg.norm(axis) > 1e-6:
        transform.RotateWXYZ(angle, axis)
    elif dot < 0:
        transform.RotateWXYZ(180, [0, 1, 0])
    transform.Scale(length, length, length)
    transform.Translate(-0.5, 0, 0)
    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetTransform(transform)
    transform_filter.SetInputConnection(arrow.GetOutputPort())
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(transform_filter.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().LightingOff() 
    return actor

t1, t2 = np.radians(GOC_BAT_DAU_DEG), np.radians(GOC_KET_THUC_DEG)
pts = np.array([
    [BAN_KINH_TRONG*np.cos(t1), BAN_KINH_TRONG*np.sin(t1), CHIEU_CAO_MIN],
    [BAN_KINH_TRONG*np.cos(t2), BAN_KINH_TRONG*np.sin(t2), CHIEU_CAO_MIN],
    [BAN_KINH_NGOAI*np.cos(t2), BAN_KINH_NGOAI*np.sin(t2), CHIEU_CAO_MIN],
    [BAN_KINH_NGOAI*np.cos(t1), BAN_KINH_NGOAI*np.sin(t1), CHIEU_CAO_MIN],
    [BAN_KINH_TRONG*np.cos(t1), BAN_KINH_TRONG*np.sin(t1), CHIEU_CAO_MAX],
    [BAN_KINH_TRONG*np.cos(t2), BAN_KINH_TRONG*np.sin(t2), CHIEU_CAO_MAX],
    [BAN_KINH_NGOAI*np.cos(t2), BAN_KINH_NGOAI*np.sin(t2), CHIEU_CAO_MAX],
    [BAN_KINH_NGOAI*np.cos(t1), BAN_KINH_NGOAI*np.sin(t1), CHIEU_CAO_MAX]
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
actor.GetProperty().SetColor(MAU_VO_VOXEL)
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

dir_R = face_centers[1] - face_centers[0]
dir_Theta = face_centers[3] - face_centers[2]
dir_Z = face_centers[5] - face_centers[4]
pos_dirs = [dir_R, dir_R, dir_Theta, dir_Theta, dir_Z, dir_Z]

for i, f_center in enumerate(face_centers):
    if i == 0 and not show_r0: continue
    if i == 1 and not show_r1: continue
    if i == 2 and not show_theta0: continue
    if i == 3 and not show_theta1: continue
    if i == 4 and not show_z0: continue
    if i == 5 and not show_z1: continue

    vec_full = f_center - center_node
    L = np.linalg.norm(vec_full)
    u = vec_full / L
    
    p_rel_start = center_node + u * (L * 0.15)
    p_rel_end   = center_node + u * (L * 0.45)
    p_mmf_center = center_node + u * (L * 0.80)
    
    renderer.AddActor(create_oriented_cylinder(p_rel_start, p_rel_end, BAN_KINH_TU_TRO, MAU_TU_TRO))
    renderer.AddActor(create_sphere(p_mmf_center, BAN_KINH_NGUON_MMF, MAU_NGUON_MMF, opacity=DO_TRONG_SUOT_NGUON_MMF))
    renderer.AddActor(create_arrow(p_mmf_center, pos_dirs[i], BAN_KINH_NGUON_MMF * 1.8, MAU_MUI_TEN))
    renderer.AddActor(create_oriented_cylinder(center_node + u*BAN_KINH_NUT_TRUNG_TAM, p_rel_start, BAN_KINH_NHANH_DAN, MAU_NHANH_DAN))
    renderer.AddActor(create_oriented_cylinder(p_rel_end, p_mmf_center - u*BAN_KINH_NGUON_MMF, BAN_KINH_NHANH_DAN, MAU_NHANH_DAN))
    renderer.AddActor(create_oriented_cylinder(p_mmf_center + u*BAN_KINH_NGUON_MMF, f_center, BAN_KINH_NHANH_DAN, MAU_NHANH_DAN))

render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(2000, 2000)
render_window.SetWindowName("Single Voxel MRN - VTK (Fixed Camera Position)")
render_window.SetMultiSamples(16)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

camera = renderer.GetActiveCamera()
renderer.ResetCamera()

# Thiết lập vị trí Camera mặc định từ hình ảnh
camera.SetPosition(CAM_POS_X, CAM_POS_Y, CAM_POS_Z)
camera.SetFocalPoint(center_node) # Hướng camera vào tâm phần tử
camera.Zoom(MUC_ZOOM_BAN_DAU)

text_actor = vtk.vtkTextActor()
text_actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
text_actor.SetPosition(0.01, 0.88)
text_actor.GetTextProperty().SetFontSize(16)
text_actor.GetTextProperty().SetColor(0.0, 0.0, 0.0)
renderer.AddActor2D(text_actor)

def update_camera_info(obj=None, event=None):
    pos = camera.GetPosition()
    info = f"Camera Position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})"
    text_actor.SetInput(info)
    render_window.Render()

def on_key_press(obj, event):
    key = obj.GetKeySym()
    if key == "Up": camera.Elevation(BUOC_CHINH_GOC)
    elif key == "Down": camera.Elevation(-BUOC_CHINH_GOC)
    elif key == "Left": camera.Azimuth(BUOC_CHINH_GOC)
    elif key == "Right": camera.Azimuth(-BUOC_CHINH_GOC)
    update_camera_info()

interactor.AddObserver('KeyPressEvent', on_key_press)
interactor.AddObserver('EndInteractionEvent', update_camera_info)

update_camera_info()
render_window.Render()
interactor.Start()