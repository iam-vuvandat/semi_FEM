def toggle_play(viewer_state): 
    if viewer_state.has_results and viewer_state.total_frames > 0:
        viewer_state.is_playing = not viewer_state.is_playing
        if viewer_state.is_playing:
            viewer_state.timer.start(100)
        else:
            viewer_state.timer.stop()