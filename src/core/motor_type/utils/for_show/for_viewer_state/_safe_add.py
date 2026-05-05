def _safe_add(viewer_state, mesh, **kwargs):
    kwargs['reset_camera'] = False
    viewer_state.pl.add_mesh(mesh, **kwargs)