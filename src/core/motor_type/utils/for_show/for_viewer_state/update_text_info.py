def update_text_info(viewer_state):
    st = lambda s, p, m: f"ON [{p}/{m-1}]" if s else "OFF"
    frame_txt = "No Results (Unsolved)" if (not viewer_state.has_results or viewer_state.total_frames == 0) else f"{viewer_state.current_frame + 1} / {viewer_state.total_frames}"
    info_left = f"Frame: {frame_txt}\nSym: {'ON' if viewer_state.use_symmetry else 'OFF'}\n" \
                f"R: {st(viewer_state.show_i, viewer_state.pos_i, viewer_state.max_i)}\n" \
                f"Th: {st(viewer_state.show_j, viewer_state.pos_j, viewer_state.max_j)}\n" \
                f"Z: {st(viewer_state.show_k, viewer_state.pos_k, viewer_state.max_k)}"
    viewer_state.pl.add_text(info_left, position="upper_left", font_size=9, name="info_text", color='black')
    total_elements = viewer_state.active_grid.n_cells 
    grid_dims = f"{viewer_state.max_i} x {viewer_state.max_j} x {viewer_state.max_k}"
    info_right = f"Total Elements: {total_elements}\nGrid: {grid_dims}"
    viewer_state.pl.add_text(info_right, position="upper_right", font_size=9, name="grid_info_text", color='black')
    viewer_state.update_camera_info()