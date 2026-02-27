import paths
import sys
import multiprocessing
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.ui.main_window.core.main_window import MainWindow

if __name__ == "__main__":
    multiprocessing.freeze_support()
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    window = MainWindow()
    window.setWindowState(Qt.WindowMaximized)
    window.show()

    sys.exit(app.exec_())
  



#pyinstaller --noconfirm --window --clean --name "semiFEM" --icon "src/ui/assets/logo.png" --add-data "src;src" --paths "src" --collect-submodules scipy --collect-all pyvista --collect-all vtk --collect-all pyvistaqt --hidden-import scipy.sparse.csgraph._validation --hidden-import scipy.special._cdflib --hidden-import PyQt5.sip --exclude-module PySide2 --exclude-module PySide6 main.py 