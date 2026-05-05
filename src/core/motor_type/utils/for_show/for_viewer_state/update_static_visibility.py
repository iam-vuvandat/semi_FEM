def update_static_visibility(viewer_state):
    if viewer_state.geometry_obj:
        for idx in range(len(viewer_state.geometry_obj.geometry)):
            if f"geo_full_{idx}" in viewer_state._actors: 
                viewer_state._actors[f"geo_full_{idx}"].SetVisibility(viewer_state.show_geometry and viewer_state.use_symmetry)
            if f"geo_sec_{idx}" in viewer_state._actors: 
                viewer_state._actors[f"geo_sec_{idx}"].SetVisibility(viewer_state.show_geometry and not viewer_state.use_symmetry)
    if "static_mesh_wire" in viewer_state._actors: 
        viewer_state._actors["static_mesh_wire"].SetVisibility(viewer_state.show_mesh_lines)
    for n in ['axis_z', 'axis_r', 'axis_arc', 'axis_tip_th']:
        if n in viewer_state._actors: 
            viewer_state._actors[n].SetVisibility(viewer_state.show_axes)
    if hasattr(viewer_state.pl, '_labels_actor') and viewer_state.pl._labels_actor:
        viewer_state.pl._labels_actor.SetVisibility(viewer_state.show_axes)
    viewer_state.pl.render()