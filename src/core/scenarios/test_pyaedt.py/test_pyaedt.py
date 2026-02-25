import paths
import numpy as np
import math 
import matplotlib.pyplot as plt
pi = math.pi

from src.core.motor_type.utils.for_export_maxwell.init_window import init_window
from src.core.motor_type.utils.for_export_maxwell.create_coil import create_coil
from src.core.motor_type.utils.for_export_maxwell.init_project import init_project
from src.core.motor_type.utils.for_axial_flux_motor_type_1.for_export_maxwell.create_balloon import create_balloon

def test_simple_coil():
    init_window()
    init_project()
    # Thong so gia lap ranh Stator
    r_in = 30.0
    r_out = 70.0
    z1 = 12.45
    z2 = 26.55
    
    ang1 = math.radians(10)
    ang2 = math.radians(40)
    ang_mid = (ang1 + ang2) / 2 # Goc trung gian de tao bac thang

    # --- RÃNH 1 ---
    p1_in  = [r_in * math.cos(ang1), r_in * math.sin(ang1), z1]
    p1_out = [r_out * math.cos(ang1), r_out * math.sin(ang1), z1]

    # --- ĐẦU NỐI NGOÀI (Tách chuyển động XY và chuyển động Z) ---
    p_out_mid1 = [r_out * math.cos(ang_mid), r_out * math.sin(ang_mid), z1]
    p_out_mid2 = [r_out * math.cos(ang_mid), r_out * math.sin(ang_mid), z2]

    # --- RÃNH 2 ---
    p2_out = [r_out * math.cos(ang2), r_out * math.sin(ang2), z2]
    p2_in  = [r_in * math.cos(ang2), r_in * math.sin(ang2), z2]

    # --- ĐẦU NỐI TRONG (Tách chuyển động XY và chuyển động Z) ---
    p_in_mid2 = [r_in * math.cos(ang_mid), r_in * math.sin(ang_mid), z2]
    p_in_mid1 = [r_in * math.cos(ang_mid), r_in * math.sin(ang_mid), z1]

    # Ghep 8 diem thanh quy dao hoan chinh
    full_points = [p1_in, p1_out, p_out_mid1, p_out_mid2, p2_out, p2_in, p_in_mid2, p_in_mid1]

    # === VẼ ĐỒ THỊ KIỂM TRA MATPLOTLIB ===
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    plot_points = full_points + [full_points[0]]
    x = [p[0] for p in plot_points]
    y = [p[1] for p in plot_points]
    z = [p[2] for p in plot_points]
    
    ax.plot(x, y, z, marker='o', linestyle='-', color='b', linewidth=2)
    
    ax.plot([x[2], x[3]], [y[2], y[3]], [z[2], z[3]], color='red', linewidth=3)
    ax.plot([x[6], x[7]], [y[6], y[7]], [z[6], z[7]], color='red', linewidth=3)
    
    for i, p in enumerate(full_points):
        ax.text(p[0], p[1], p[2], f' P{i+1}', color='black', fontsize=10, fontweight='bold')
        
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.title('3D Planar-Bend Coil Path (Orthogonal Routing)')
    plt.show()

    # === DỰNG HÌNH MAXWELL ===
    init_window()
    m3d = init_project(project_name="Complex_Wavy_Coil", solution_type="Transient")
        
    coil_width = 4.0
    
    # CHI TIẾT QUYẾT ĐỊNH: Dùng tiết diện TRÒN đe lướt qua góc gập sắc nhọn
    coil_solid, coil_exc_obj = create_coil(
        m3d=m3d, 
        points=full_points, 
        width=coil_width,
        current="5A",
        conductors_number=25,
        shape="round" 
    )
    
    create_balloon(50, m3d)
    
    phase1_obj = m3d.assign_winding(winding_type='Current', is_solid=False, current="5*sin(Time*2)A", name="Phase_A")
    
    m3d.add_winding_coils(assignment=phase1_obj.name, coils=coil_exc_obj.name)
    
    print(f"SUCCESS: Linked '{coil_exc_obj.name}' to '{phase1_obj.name}'")

if __name__ == "__main__":
    test_simple_coil()