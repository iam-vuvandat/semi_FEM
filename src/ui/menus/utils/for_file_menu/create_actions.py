import paths
from PyQt5.QtWidgets import QAction, QStyle, QFileDialog, QMessageBox
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt

# Import module motor_io
from src.core.storage.core import motor_io
# Class motor
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1

def create_actions(file_menu):
    main_window = file_menu.main_window

    def handle_new():
        """Tạo motor mới và làm mới UI"""
        main_window.motor = AxialFluxMotorType1()
        # Không gọi motor.reload(), chỉ reload UI để nhận đối tượng mới
        main_window.reload()
        main_window.statusBar().showMessage("New project initialized.", 3000)

    def handle_open():
        """Nạp motor và hiển thị trạng thái nạp"""
        path, _ = QFileDialog.getOpenFileName(
            main_window, "Open Motor Design", "", "MBGRN Files (*.mbgrn)"
        )
        if path:
            def load_cb(msg):
                main_window.statusBar().showMessage(msg)
                main_window.repaint() 

            loaded_motor = motor_io.load_motor(filename="", filepath=path, callback=load_cb)
            
            if loaded_motor:
                main_window.motor = loaded_motor
                # Làm mới UI để hiển thị dữ liệu từ file vừa nạp
                main_window.reload()
                main_window.statusBar().showMessage(f"Successfully loaded: {path}", 5000)
            else:
                QMessageBox.critical(main_window, "Error", "Failed to load motor data.")

    def handle_save():
        """Lưu motor và cảnh báo trên StatusBar"""
        if main_window.motor is None:
            QMessageBox.warning(main_window, "Warning", "Nothing to save!")
            return

        path, _ = QFileDialog.getSaveFileName(
            main_window, "Save Motor Design", "", "MBGRN Files (*.mbgrn)"
        )
        
        if path:
            main_window.statusBar().setStyleSheet("color: red; font-weight: bold;")
            main_window.statusBar().showMessage("SAVING... PLEASE DO NOT CLOSE THE APPLICATION!", 0)
            main_window.repaint() 

            def save_cb(msg):
                main_window.statusBar().showMessage(f"Saving: {msg}")
                main_window.repaint()

            success = motor_io.save_motor(
                main_window.motor, 
                filename="", 
                filepath=path, 
                callback=save_cb
            )

            main_window.statusBar().setStyleSheet("") 
            if success:
                main_window.statusBar().showMessage(f"Project saved successfully: {path}", 5000)
            else:
                main_window.statusBar().showMessage("Save failed!", 5000)
                QMessageBox.critical(main_window, "Error", "Failed to save data.")

    # --- KHỞI TẠO ACTIONS ---
    file_menu.new_act = QAction(file_menu.style().standardIcon(QStyle.SP_FileIcon), "New", file_menu)
    file_menu.new_act.setShortcut(QKeySequence.New)
    file_menu.new_act.triggered.connect(handle_new)
    
    file_menu.open_act = QAction(file_menu.style().standardIcon(QStyle.SP_DialogOpenButton), "Open...", file_menu)
    file_menu.open_act.setShortcut(QKeySequence.Open)
    file_menu.open_act.triggered.connect(handle_open)
    
    file_menu.save_act = QAction(file_menu.style().standardIcon(QStyle.SP_DialogSaveButton), "Save", file_menu)
    file_menu.save_act.setShortcut(QKeySequence.Save)
    file_menu.save_act.triggered.connect(handle_save)
    
    file_menu.exit_act = QAction("Exit", file_menu)
    file_menu.exit_act.setShortcut("Alt+F4")
    file_menu.exit_act.triggered.connect(main_window.close)

    # Thêm vào Menu
    file_menu.addAction(file_menu.new_act)
    file_menu.addAction(file_menu.open_act)
    file_menu.addSeparator()
    file_menu.addAction(file_menu.save_act)
    file_menu.addSeparator()
    file_menu.addAction(file_menu.exit_act)