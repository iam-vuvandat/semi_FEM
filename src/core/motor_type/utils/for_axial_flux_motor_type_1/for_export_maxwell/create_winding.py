import numpy as np
import math
from src.core.motor_type.utils.for_create_geometry.rotate_point_z import rotate_point_z
from src.core.motor_type.utils.for_export_maxwell.create_coil import create_coil

def create_winding(motor, m3d):
    st_geo = motor.geometry_data.stator
    ro_geo = motor.geometry_data.rotor
    slot_num = st_geo.slot_number
    st_lam_dia = st_geo.stator_lam_dia * 1e3
    st_bore_dia = st_geo.stator_bore_dia * 1e3
    sl_width, sl_depth = st_geo.slot_width * 1e3, st_geo.slot_depth * 1e3
    
    slot_arc = 360 / slot_num
    r_out, r_in = st_lam_dia / 2, st_bore_dia / 2

    wdg_data = motor.winding_data
    sl_matrix = wdg_data.slot_matrix
    throw, phase, layers = int(wdg_data.throw), int(wdg_data.phase), int(wdg_data.winding_layer)
    
    wire_rad = min(sl_depth / (throw + 2), sl_width) * 0.3 * 0.5 * 0.5
    
    offset_z0 = (ro_geo.rotor_length + ro_geo.magnet_length + ro_geo.airgap) * 1e3
    clearance = wire_rad * 1.2
    z_start_layer = offset_z0 + clearance
    z_end_layer = (offset_z0 + sl_depth) - clearance
    
    z_layers = np.linspace(z_start_layer, z_end_layer, layers).tolist() if layers > 1 else [z_start_layer, z_start_layer]

    ext = 2.5 * wire_rad
    r_in_ext, r_out_ext = r_in - ext, r_out + ext

    if sl_matrix is not None:
        for p_idx in range(phase):
            for s_idx in range(int(slot_num)):
                if sl_matrix[s_idx, p_idx] > 0:
                    t_idx = (s_idx + throw) % int(slot_num)
                    ang_s = (s_idx * slot_arc) + (slot_arc / 2)
                    ang_t = (t_idx * slot_arc) + (slot_arc / 2)

                    p1_in  = list(rotate_point_z([r_in_ext, 0, z_layers[0]], ang_s))
                    p1_out = list(rotate_point_z([r_out_ext, 0, z_layers[0]], ang_s))
                    p2_out = list(rotate_point_z([r_out_ext, 0, z_layers[1]], ang_t))
                    p2_in  = list(rotate_point_z([r_in_ext, 0, z_layers[1]], ang_t))
                    
                    print("\n" + "="*50)
                    print(f"KET QUA 4 DIEM CUA COIL DAU TIEN (Phase {p_idx}, Slot {s_idx}):")
                    print("Copy mang duoi day vao file test_pyaedt.py:")
                    print("full_points = [")
                    print(f"    {p1_in},")
                    print(f"    {p1_out},")
                    print(f"    {p2_out},")
                    print(f"    {p2_in}")
                    print("]")
                    print("="*50 + "\n")
                    
                    # Return ngay lap tuc sau khi print coil dau tien de Dat test
                    return "Da in 4 diem ra terminal."

    return "Khong tim thay du lieu cuon day."