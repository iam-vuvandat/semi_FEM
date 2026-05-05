def toggle_symmetry_btn(viewer_state, state):
    if viewer_state.sym_factor <= 1: return
    viewer_state.use_symmetry = state
    viewer_state._update_limits()
    viewer_state._redraw_wireframe()
    viewer_state.update_static_visibility()
    viewer_state.render()