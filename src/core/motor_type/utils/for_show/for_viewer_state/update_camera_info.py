import numpy as np

def update_camera_info(viewer_state):
    pos = np.array(viewer_state.pl.camera.position)
    current_pos = (round(pos[0], 6), round(pos[1], 6), round(pos[2], 6))
    if viewer_state._last_cam_pos == current_pos:
        return
    viewer_state._last_cam_pos = current_pos
    cam_text = f"Camera: X {current_pos[0]:.6f}, Y {current_pos[1]:.6f}, Z {current_pos[2]:.6f}"
    viewer_state.pl.add_text(cam_text, position="lower_right", font_size=8, name="camera_info", color='black')