def toggle_axes_btn(viewer_state, s): 
    viewer_state.show_axes = s
    viewer_state.update_static_visibility()