def _redraw_wireframe(viewer_state):
    if "static_mesh_wire" in viewer_state._actors: 
        viewer_state.pl.remove_actor("static_mesh_wire")
    viewer_state.pl.add_mesh(viewer_state.active_grid, style='wireframe', color='black', opacity=0.05, 
                line_width=1, name="static_mesh_wire")
    if "static_mesh_wire" in viewer_state._actors:
        viewer_state._actors["static_mesh_wire"].SetVisibility(viewer_state.show_mesh_lines)