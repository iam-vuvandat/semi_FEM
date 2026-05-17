import numpy as np

def create_airgap_probe_line(m3d, motor):
    # geometry data extract
    inner_radius = (motor.geometry_data.stator.stator_bore_dia / 2) * 1e3 # unit: mm
    outer_radius = (motor.geometry_data.stator.stator_lam_dia / 2) * 1e3 # unit: mm

    # require motor property
    motor.require('mechanical')
    symmetry_factor = motor.mechanical.symmetry_factor
    angle_begin = 0.0 # unit: rad
    angle_end   = np.pi * 2 / symmetry_factor
    z_position = 0.0 # airgap plane at 0xy plane

    r_avg = (inner_radius + outer_radius) / 2
    angle_mid = (angle_begin + angle_end) / 2

    x1 = r_avg * np.cos(angle_begin)
    y1 = r_avg * np.sin(angle_begin)

    x2 = r_avg * np.cos(angle_mid)
    y2 = r_avg * np.sin(angle_mid)

    x3 = r_avg * np.cos(angle_end)
    y3 = r_avg * np.sin(angle_end)

    points = [
        [x1, y1, z_position],
        [x2, y2, z_position],
        [x3, y3, z_position]
    ]

    m3d.modeler.create_polyline(
        points=points,
        segment_type="Arc",
        name="Airgap_Probe_Line",
        non_model=True
    )

    return True