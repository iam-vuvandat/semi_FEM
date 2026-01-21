import paths
from PyQt5.QtWidgets import QMenuBar, QMenu, QAction, QStyle,QMainWindow
from PyQt5.QtGui import QKeySequence

from src.ui.menus.utils.for_main_menu.create_main_menu import create_main_menu

class MainMenu(QMenuBar):
    def __init__(self, main_window=None):
        super().__init__(main_window) 
        self.main_window = main_window
        self.file_menu = None

        create_main_menu(main_menu=self)



