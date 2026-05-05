def toggle_bmap_btn(viewer_state, state):
    if not viewer_state.has_results or viewer_state.total_frames == 0:
        viewer_state.bmap_mode = False
        if viewer_state.ref_act_bmap: viewer_state.ref_act_bmap.setChecked(False)
        return
    viewer_state.bmap_mode = state
    if state:
        viewer_state.show_geometry = False
        if viewer_state.ref_act_geo: viewer_state.ref_act_geo.setChecked(False)
        viewer_state.update_static_visibility()
    viewer_state.render()