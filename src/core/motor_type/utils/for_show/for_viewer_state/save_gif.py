from PyQt5.QtWidgets import QFileDialog

def save_gif(viewer_state):
        if not viewer_state.has_results or viewer_state.total_frames == 0: return
        was = viewer_state.is_playing; viewer_state.timer.stop(); viewer_state.is_playing = False
        f, _ = QFileDialog.getSaveFileName(viewer_state.pl.app_window, "Save", "anim.gif", "GIF (*.gif)")
        if f:
            viewer_state.pl.open_gif(f)
            for i in range(viewer_state.total_frames): viewer_state.current_frame = i; viewer_state.render(); viewer_state.pl.write_frame()
            viewer_state.pl.close()
        if was: viewer_state.toggle_play()