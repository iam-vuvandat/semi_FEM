import numpy as np
import pyvista as pv

def _add_cylindrical_axes_static(pl, length=100):
    origin = np.array([0, 0, 0])
    arrow_params = {'tip_length': 0.15, 'tip_radius': 0.04, 'shaft_radius': 0.015, 'scale': length}
    
    for n in ['axis_z', 'axis_r', 'axis_arc', 'axis_tip_th']:
        if n in pl.renderer.actors: pl.remove_actor(n)
    if hasattr(pl, '_labels_actor') and pl._labels_actor:
        pl.remove_actor(pl._labels_actor)

    pl.add_mesh(pv.Arrow(start=origin, direction=[0, 0, 1], **arrow_params), 
                color='#2980B9', name='axis_z', lighting=False)
    pl.add_mesh(pv.Arrow(start=origin, direction=[1, 0, 0], **arrow_params), 
                color='#C0392B', name='axis_r', lighting=False)
    
    radius_theta = length * 0.8
    angle = np.deg2rad(45)
    p_end = [radius_theta * np.cos(angle), radius_theta * np.sin(angle), 0]
    pl.add_mesh(pv.CircularArc(pointa=[radius_theta, 0, 0], pointb=p_end, center=origin), 
                color='#27AE60', line_width=4, name='axis_arc')

    tangent_dir = [-np.sin(angle), np.cos(angle), 0]
    theta_tip = pv.Cone(center=p_end, direction=tangent_dir, height=length * 0.08, radius=length * 0.025)
    pl.add_mesh(theta_tip, color='#27AE60', lighting=False, name='axis_tip_th')

    offset = length * 0.1
    points = [
        origin - np.array([offset*0.5, offset*0.5, 0]),
        np.array([0, 0, length + offset]),
        np.array([length + offset, 0, 0]),
        np.array([p_end[0] + offset*0.5, p_end[1] + offset*0.5, 0])
    ]
    labels = ["O", "z", "r", "Th"]
    lbl_actor = pl.add_point_labels(points, labels, font_size=24, text_color='black',
                                    show_points=False, always_visible=True, shape=None, name='axis_labels')
    pl._labels_actor = lbl_actor