import numpy as np

def _rescale_camera(viewer_state):
    pos = np.array(viewer_state.pl.camera_position[0])
    focal = np.array(viewer_state.pl.camera_position[1])
    direction = pos - focal
    direction = direction / np.linalg.norm(direction)
    new_pos = focal + direction * viewer_state.dist_factor
    viewer_state.pl.camera_position = [new_pos, focal, viewer_state.pl.camera_position[2]]
    viewer_state.render()