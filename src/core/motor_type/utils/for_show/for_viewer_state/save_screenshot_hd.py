from PyQt5.QtWidgets import QFileDialog

def save_screenshot_hd(viewer_state):
        old_bg = viewer_state.pl.background_color
        viewer_state.pl.set_background("white")
        f, _ = QFileDialog.getSaveFileName(viewer_state.pl.app_window, "Save HD Image", "motor_hd.png", "PNG (*.png)")
        if f: viewer_state.pl.screenshot(f, transparent_background=False, scale=4)
        viewer_state.pl.set_background(old_bg)