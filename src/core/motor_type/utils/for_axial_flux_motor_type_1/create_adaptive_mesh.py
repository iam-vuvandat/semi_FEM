import numpy as np
import math

from src.core.core_class.models.CylindricalMesh import CylindricalMesh
pi = math.pi

def create_adaptive_mesh(motor):
    stator = motor.geometry_data.stator
    rotor = motor.geometry_data.rotor
    md = motor.adaptive_mesh_data

    def f_c(n):
        return max(1, int(n))

    rl1 = rotor.rotor_lam_dia / 2 - rotor.magnet_embed_depth - rotor.magnet_depth - rotor.shaft_hole_diameter / 2
    rl2 = rotor.magnet_depth
    rl3 = rotor.magnet_embed_depth
    
    if rl1 <= 0: rl1 = 0
    if rl3 <= 0: rl3 = 0

    nr_in = f_c(md.n_r_in)
    nr1 = f_c(md.n_r_1) if rl1 > 0 else 0
    nr2 = f_c(md.n_r_2)
    nr3 = f_c(md.n_r_3) if rl3 > 0 else 0
    nr_out = f_c(md.n_r_out)
    n_theta = f_c(md.n_theta)

    radial_segments = []
    radial_min = rotor.shaft_hole_diameter/2 if stator.stator_bore_dia > rotor.shaft_hole_diameter else stator.stator_bore_dia/2

    r_curr = radial_min * 0.9
    r_inner = np.linspace(r_curr, rotor.shaft_hole_diameter / 2, nr_in + 1)
    radial_segments.append(r_inner)
    r_curr = r_inner[-1]

    if nr1 > 0:
        r_reg1 = np.linspace(r_curr, r_curr + rl1, nr1 + 1)
        radial_segments.append(r_reg1[1:])
        r_curr = r_reg1[-1]
    else:
        r_curr += rl1

    r_reg2 = np.linspace(r_curr, r_curr + rl2, nr2 + 1)
    radial_segments.append(r_reg2[1:])
    r_curr = r_reg2[-1]

    if nr3 > 0:
        r_reg3 = np.linspace(r_curr, r_curr + rl3, nr3 + 1)
        radial_segments.append(r_reg3[1:])
        r_curr = r_reg3[-1]
    else:
        r_curr += rl3

    r_outer = np.linspace(r_curr, r_curr * 1.1, nr_out + 1)
    radial_segments.append(r_outer[1:])
    radial_coordinates = np.concatenate(radial_segments)

    if md.use_symmetry_factor: 
        theta_max = 2 * pi / motor.symmetry_factor
        theta_coordinates = np.linspace(0, theta_max, n_theta + 1)
    else:
        theta_coordinates = np.linspace(0, 2 * pi, n_theta + 1)

    sy_h = stator.stator_length - stator.tooth_tip_depth - stator.slot_depth
    tt_w = (1/2) * (stator.slot_width - stator.slot_opening)
    tt_h = tt_w * np.tan(np.radians(stator.tooth_tip_angle))

    nz_ia = f_c(md.n_z_in_air)
    nz_ry = f_c(md.n_z_rotor_yoke)
    nz_mg = f_c(md.n_z_magnet)
    nz_ag = f_c(md.n_z_airgap)
    nz_t1 = f_c(md.n_z_tooth_tip_1)
    nz_t2 = f_c(md.n_z_tooth_tip_2)
    nz_tb = f_c(md.n_z_tooth_body)
    nz_sy = f_c(md.n_z_stator_yoke)
    nz_oa = f_c(md.n_z_out_air)

    axial_segments = []
    z_ia = np.linspace(-rotor.rotor_length, 0, nz_ia + 1)
    axial_segments.append(z_ia)
    z_curr = z_ia[-1]

    z_ry = np.linspace(z_curr, z_curr + rotor.rotor_length, nz_ry + 1)
    axial_segments.append(z_ry[1:])
    z_curr = z_ry[-1]

    z_mg = np.linspace(z_curr, z_curr + rotor.magnet_length, nz_mg + 1)
    axial_segments.append(z_mg[1:])
    z_curr = z_mg[-1]

    z_ag = np.linspace(z_curr, z_curr + rotor.airgap, nz_ag + 1)
    axial_segments.append(z_ag[1:])
    z_curr = z_ag[-1]

    z_t1 = np.linspace(z_curr, z_curr + stator.tooth_tip_depth, nz_t1 + 1)
    if nz_t1 >= 1:
        axial_segments.append(z_t1[1:])
    z_pos_5 = z_t1[-1]

    z_t2 = np.linspace(z_pos_5, z_pos_5 + tt_h, nz_t2 + 1)
    axial_segments.append(z_t2[1:])
    
    z_tb = np.linspace(z_pos_5, z_pos_5 + stator.slot_depth, nz_tb + 1)
    axial_segments.append(z_tb[1:])
    z_curr = z_tb[-1]

    z_sy = np.linspace(z_curr, z_curr + sy_h, nz_sy + 1)
    axial_segments.append(z_sy[1:])
    z_curr = z_sy[-1]

    z_oa = np.linspace(z_curr, z_curr + sy_h, nz_oa + 1)
    axial_segments.append(z_oa[1:])

    axial_coordinates = np.concatenate(axial_segments)
    
    return CylindricalMesh(r_nodes = radial_coordinates,
                           theta_nodes = theta_coordinates,
                           z_nodes = axial_coordinates,
                           periodic_boundary = md.periodic_boundary,
                           adaptive_mesh_data = md)