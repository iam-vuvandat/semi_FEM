import numpy as np
from src.core.motor_type.utils.for_show._add_cylindrical_axes_static import _add_cylindrical_axes_static

def resize_axes(viewer_state, sign):
    step = 0.1
    viewer_state.axes_scale = np.clip(viewer_state.axes_scale + sign * step, 0.1, 5.0)
    new_len = viewer_state.base_axes_len * viewer_state.axes_scale
    _add_cylindrical_axes_static(viewer_state.pl, new_len)
    viewer_state.update_static_visibility()