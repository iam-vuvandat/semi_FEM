from core_class.models.CylindricalMesh import CylindricalMesh
import numpy as np
import math

pi = math.pi

def create_adaptive_mesh(motor,
                         n_r_in=3,
                         n_r_1=4,
                         n_r_2=4,
                         n_r_3=4,
                         n_r_out=3,
                         n_theta=180,
                         n_z_in_air=3,
                         n_z_rotor_yoke=4,
                         n_z_magnet=4,
                         n_z_airgap=5,
                         n_z_tooth_tip_1=1,
                         n_z_tooth_tip_2=4,
                         n_z_tooth_body=4,
                         n_z_stator_yoke=3,
                         n_z_out_air=3,
                         use_symmetry_factor=True,
                         periodic_boundary=True):
    
    # initial check
    if motor.magnet_embed_depth == 0:
        n_r_3 = -1

    if motor.rotor_lam_dia / 2 - motor.magnet_embed_depth - motor.magnet_depth == motor.shaft_hole_diameter:
        n_r_1 = - 1 

    r_segments = []
    
    r_min = motor.shaft_hole_diameter/2 if motor.stator_bore_dia > motor.shaft_hole_diameter else motor.stator_bore_dia/2
    
    r_max = motor.stator_lam_dia/2 if motor.stator_lam_dia > motor.rotor_lam_dia else motor.rotor_lam_dia/2

    # Chiều dài vật lý của các phân đoạn R
    L_r_1 = motor.rotor_lam_dia / 2 - motor.magnet_embed_depth - motor.magnet_depth - motor.shaft_hole_diameter / 2
    L_r_2 = motor.magnet_depth
    L_r_3 = motor.magnet_embed_depth

    # 1. r_in
    if n_r_in > 0:
        r_in = np.linspace(r_min * 0.9, motor.shaft_hole_diameter / 2, n_r_in)
        r_segments.append(r_in)
        R_start_1 = r_in[-1]
    else:
        R_start_1 = motor.shaft_hole_diameter / 2

    # 2. r_1
    if n_r_1 > 0:
        r_1 = np.linspace(R_start_1, R_start_1 + L_r_1, n_r_1)
        r_segments.append(r_1[1:])
        R_start_2 = r_1[-1]
    else:
        R_start_2 = R_start_1 + L_r_1

    # 3. r_2
    if n_r_2 > 0:
        r_2 = np.linspace(R_start_2, R_start_2 + L_r_2, n_r_2)
        r_segments.append(r_2[1:])
        R_start_3 = r_2[-1]
    else:
        R_start_3 = R_start_2 + L_r_2

    # 4. r_3
    if n_r_3 > 0:
        r_3 = np.linspace(R_start_3, R_start_3 + L_r_3, n_r_3)
        r_segments.append(r_3[1:])
        R_start_out = r_3[-1]
    else:
        R_start_out = R_start_3 + L_r_3

    # 5. r_out
    if n_r_out > 0:
        r_out = np.linspace(R_start_out, R_start_out * 1.1, n_r_out)
        r_segments.append(r_out[1:])

    r_cordinate = np.concatenate(r_segments)

    # --- Theta ---
    if use_symmetry_factor == True: 
        symmetry_factor = motor.symmetry_factor
        theta_min = 0 
        theta_max = 2*pi / symmetry_factor
        theta_cordinate = np.linspace(theta_min, theta_max, n_theta)
    else:
        theta_cordinate = np.linspace(0, 2*pi, n_theta)

    # --- Axial (Z) ---
    z_segments = []
    
    L_stator_yoke = motor.stator_length - motor.tooth_tip_depth - motor.slot_depth
    w1 = (1/2) * (motor.slot_width - motor.slot_opening)
    h1 = w1 * np.tan(np.radians(motor.tooth_tip_angle))

    # 1. z_air_in
    if n_z_in_air > 0:
        z_air_in = np.linspace(-motor.rotor_length, 0, n_z_in_air)
        z_segments.append(z_air_in)
        Z_start_1 = z_air_in[-1]
    else:
        Z_start_1 = 0

    # 2. z_rotor_yoke
    if n_z_rotor_yoke > 0:
        z_rotor_yoke_cordinate = np.linspace(Z_start_1, Z_start_1 + motor.rotor_length, n_z_rotor_yoke)
        z_segments.append(z_rotor_yoke_cordinate[1:])
        Z_start_2 = z_rotor_yoke_cordinate[-1]
    else:
        Z_start_2 = Z_start_1 + motor.rotor_length

    # 3. z_magnet
    if n_z_magnet > 0:
        z_magnet_cordinate = np.linspace(Z_start_2, Z_start_2 + motor.magnet_length, n_z_magnet)
        z_segments.append(z_magnet_cordinate[1:])
        Z_start_3 = z_magnet_cordinate[-1]
    else:
        Z_start_3 = Z_start_2 + motor.magnet_length

    # 4. z_airgap
    if n_z_airgap > 0:
        z_airgap_cordinate = np.linspace(Z_start_3, Z_start_3 + motor.airgap, n_z_airgap)
        z_segments.append(z_airgap_cordinate[1:])
        Z_start_4 = z_airgap_cordinate[-1]
    else:
        Z_start_4 = Z_start_3 + motor.airgap

    # 5. z_tooth_tip_1
    if n_z_tooth_tip_1 > 0:
        z_tooth_tip_1_cordinate = np.linspace(Z_start_4, Z_start_4 + motor.tooth_tip_depth, n_z_tooth_tip_1)
        if n_z_tooth_tip_1 > 1:
            z_segments.append(z_tooth_tip_1_cordinate[1:])
        Z_start_5 = z_tooth_tip_1_cordinate[-1]
    else:
        Z_start_5 = Z_start_4 + motor.tooth_tip_depth
        
    # 6. z_tooth_tip_2
    if n_z_tooth_tip_2 > 0:
        z_tooth_tip_2_cordinate = np.linspace(Z_start_5, Z_start_5 + h1, n_z_tooth_tip_2)
        z_segments.append(z_tooth_tip_2_cordinate[1:])
        Z_start_6 = z_tooth_tip_2_cordinate[-1]
    else:
        Z_start_6 = Z_start_5 + h1
        
    # 7. z_tooth_body (Bắt đầu từ Z_start_5 theo logic gốc)
    if n_z_tooth_body > 0:
        z_tooth_cordinate = np.linspace(Z_start_5, Z_start_5 + motor.slot_depth, n_z_tooth_body)
        z_segments.append(z_tooth_cordinate[1:])
        Z_start_7 = z_tooth_cordinate[-1]
    else:
        Z_start_7 = Z_start_5 + motor.slot_depth

    # 8. z_stator_yoke
    if n_z_stator_yoke > 0:
        z_stator_yoke_cordinate = np.linspace(Z_start_7, Z_start_7 + L_stator_yoke, n_z_stator_yoke)
        z_segments.append(z_stator_yoke_cordinate[1:])
        Z_start_8 = z_stator_yoke_cordinate[-1]
    else:
        Z_start_8 = Z_start_7 + L_stator_yoke

    # 9. z_air_out (Cùng chiều dài L_stator_yoke theo logic gốc)
    if n_z_out_air > 0:
        z_air_out = np.linspace(Z_start_8, Z_start_8 + L_stator_yoke, n_z_out_air)
        z_segments.append(z_air_out[1:])

    z_cordinate = np.concatenate(z_segments)
    
    return CylindricalMesh(r_nodes=r_cordinate,
                           theta_nodes=theta_cordinate,
                           z_nodes=z_cordinate,
                           periodic_boundary=periodic_boundary)