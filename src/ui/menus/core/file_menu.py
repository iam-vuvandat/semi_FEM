import paths
from PyQt5.QtWidgets import QMenu
from src.ui.menus.utils.for_file_menu.create_actions import create_actions

class FileMenu(QMenu):
    def __init__(self, main_menu):
        super().__init__("&File", main_menu)
        self.main_menu = main_menu
        self.main_window = self.main_menu.main_window
        
        self.new_act = None
        self.open_act = None
        self.save_act = None
        self.save_as_act = None
        self.exit_act = None
        
        create_actions(file_menu=self)