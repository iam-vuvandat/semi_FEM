import paths

from src.ui.menus.core.file_menu import FileMenu

def create_main_menu(main_menu = None):
    main_menu.file_menu = FileMenu(main_menu= main_menu)
    main_menu.addMenu(main_menu.file_menu)