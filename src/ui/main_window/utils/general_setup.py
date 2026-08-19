import sys
import ctypes
import os
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

def general_setup(main_window=None):
    try:
        myappid = 'semiFEM.v0.0.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.abspath(os.path.join(base_dir, "..", "..", "assets"))

    icon_path = os.path.join(assets_dir, "logo.png")
    app_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon()

    qss_path = os.path.join(assets_dir, "style.qss")
    qss_content = ""
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            qss_content = f.read()

    app = QApplication.instance()
    if app is not None:
        app.setWindowIcon(app_icon)
        app.setStyle(QStyleFactory.create('Fusion'))
        if qss_content:
            app.setStyleSheet(qss_content)

    if main_window is not None:
        main_window.setWindowTitle("semiFEM")
        main_window.setWindowIcon(app_icon)
        main_window.setWindowState(Qt.WindowMaximized)
        main_window.setMinimumSize(1024, 768)
        if qss_content and app is None:
            main_window.setStyleSheet(qss_content)