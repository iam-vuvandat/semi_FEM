import paths  # Module quản lý đường dẫn dự án
import sys
import ctypes
from PyQt5.QtWidgets import (QMainWindow, QWidget, QTabWidget, QApplication, 
                             QVBoxLayout, QSplitter, QAction, QStyleFactory, 
                             QStatusBar, QToolBar, QStyle)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont

from src.ui.main_window.utils.general_setup import general_setup
from src.ui.menus.core.main_menu import MainMenu
from src.ui.widget.widget.core.widget import Widget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        general_setup(main_window=self)
        self.motor = None

        self.main_menu = None
        self.widget = None

        self.reload()
        
        
    def reload(self):
        self.main_menu = MainMenu(main_window=self)
        self.setMenuBar(self.main_menu)

        self.widget = Widget(main_window=self)
        self.setCentralWidget(self.widget)


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
