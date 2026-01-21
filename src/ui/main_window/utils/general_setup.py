import ctypes
from PyQt5.QtWidgets import QApplication, QStyleFactory

def general_setup(main_window = None):
    try:
        myappid = 'hust.ee.mbgrn.3d.solver.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    if main_window is not None:
        main_window.setWindowTitle("semiFem - 3D MBGRN Solver")
        main_window.resize(1100, 850)
        QApplication.setStyle(QStyleFactory.create('Fusion'))