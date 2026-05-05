def toggle_mesh_btn(viewer_state, s): 
    viewer_state.show_mesh_lines = s
    viewer_state.update_static_visibility()