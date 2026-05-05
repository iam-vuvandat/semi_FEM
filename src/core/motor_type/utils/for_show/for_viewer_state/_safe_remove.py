def _safe_remove(viewer_state, name):
    if name in viewer_state._actors: 
        viewer_state.pl.remove_actor(name)