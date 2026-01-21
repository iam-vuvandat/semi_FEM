from PyQt5.QtWidgets import QAction, QStyle
from PyQt5.QtGui import QKeySequence

def create_actions(file_menu):
    file_menu.new_act = QAction(file_menu.style().standardIcon(QStyle.SP_FileIcon), "New", file_menu)
    file_menu.new_act.setShortcut(QKeySequence.New)
    
    file_menu.open_act = QAction(file_menu.style().standardIcon(QStyle.SP_DialogOpenButton), "Open...", file_menu)
    file_menu.open_act.setShortcut(QKeySequence.Open)
    
    file_menu.save_act = QAction(file_menu.style().standardIcon(QStyle.SP_DialogSaveButton), "Save", file_menu)
    file_menu.save_act.setShortcut(QKeySequence.Save)
    
    file_menu.exit_act = QAction("Exit", file_menu)
    file_menu.exit_act.setShortcut("Alt+F4")

    file_menu.addAction(file_menu.new_act)
    file_menu.addAction(file_menu.open_act)
    file_menu.addSeparator()
    file_menu.addAction(file_menu.save_act)
    file_menu.addSeparator()
    file_menu.addAction(file_menu.exit_act)

    file_menu.exit_act.triggered.connect(file_menu.main_window.close)