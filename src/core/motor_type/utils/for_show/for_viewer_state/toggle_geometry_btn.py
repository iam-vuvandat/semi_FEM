def toggle_geometry_btn(viewer_state, state):
    viewer_state.show_geometry = state
    if state: 
        viewer_state.bmap_mode = False
        if viewer_state.ref_act_bmap: viewer_state.ref_act_bmap.setChecked(False)
    viewer_state.update_static_visibility()
    viewer_state.render()