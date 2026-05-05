def pre_frame(viewer_state): 
    if viewer_state.has_results and viewer_state.total_frames > 0:
        viewer_state.current_frame = (viewer_state.current_frame - 1) % viewer_state.total_frames
        viewer_state.render()