import paths
from PyQt5.QtWidgets import QAction, QStyle, QFileDialog, QMessageBox
from PyQt5.QtGui import QKeySequence

# Import module motor_io bạn vừa gửi
from src.core.storage.core import motor_io
# Cần import class motor để dùng cho lệnh New
from src.core.motor_type.models.axial_flux_motor_type_1 import AxialFluxMotorType1

def create_actions(file_menu):
    main_window = file_menu.main_window

    def handle_new():
        """Tạo motor mới và làm mới UI"""
        main_window.motor = AxialFluxMotorType1()
        main_window.motor.reload() # Tính toán mặc định
        main_window.reload()
        main_window.statusBar().showMessage("New project initialized.", 3000)

    def handle_open():
        """Nạp toàn bộ object motor từ file .mbgrn"""
        path, _ = QFileDialog.getOpenFileName(
            main_window, "Open Motor Design", "", "MBGRN Files (*.mbgrn)"
        )
        if path:
            # motor_io.load_motor trả về chính object motor đã lưu
            loaded_motor = motor_io.load_motor(filename="", filepath=path)
            if loaded_motor:
                main_window.motor = loaded_motor
                # Quan trọng: Gọi reload() để Widget và Menu nhận motor mới
                main_window.reload()
                main_window.statusBar().showMessage(f"Loaded: {path}", 3000)
            else:
                QMessageBox.critical(main_window, "Error", "Failed to load motor data.")

    def handle_save():
        """Lưu toàn bộ object motor hiện tại"""
        if main_window.motor is None:
            QMessageBox.warning(main_window, "Warning", "Nothing to save!")
            return

        path, _ = QFileDialog.getSaveFileName(
            main_window, "Save Motor Design", "", "MBGRN Files (*.mbgrn)"
        )
        if path:
            # motor_io.save_motor nhận object và đường dẫn
            success = motor_io.save_motor(main_window.motor, filename="", filepath=path)
            if success:
                main_window.statusBar().showMessage(f"Saved: {path}", 3000)
            else:
                QMessageBox.critical(main_window, "Error", "Failed to save data.")

    # --- KHỞI TẠO ACTIONS (Dựa trên khung của bạn) ---
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

    # Thêm vào Menu (Giữ nguyên thứ tự bạn đã viết)
    file_menu.addAction(file_menu.new_act)
    file_menu.addAction(file_menu.open_act)
    file_menu.addSeparator()
    file_menu.addAction(file_menu.save_act)
    file_menu.addSeparator()
    file_menu.addAction(file_menu.exit_act)