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
  


  