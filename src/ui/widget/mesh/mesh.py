import paths
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from src.ui.widget.mesh.init_ui import init_ui

class StateWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, motor, target_component):
        super().__init__()
        self.motor = motor
        self.target_component = target_component

    def run(self):
        try:
            def thread_callback(msg, *args, **kwargs):
                if args and isinstance(args[0], (int, float)):
                    self.progress.emit(f"{msg} ({args[0]}%)")
                else:
                    self.progress.emit(str(msg))

            self.motor.require(self.target_component, callback=thread_callback)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class Mesh(QWidget):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.main_window = self.parent_widget.main_window
        
        self.plotter = None
        self.current_view_mode = "mesh"
        self.status_label = None
        self.btn_mesh_view = None
        self.btn_material_view = None
        
        self.thread = None
        self.worker = None
        
        self.init_ui()

    def init_ui(self):
        return init_ui(mesh_tab=self)

    def set_ui_busy(self, busy=True):
        if self.btn_mesh_view:
            self.btn_mesh_view.setEnabled(not busy and self.current_view_mode != "mesh")
        if self.btn_material_view:
            self.btn_material_view.setEnabled(not busy and self.current_view_mode != "material")

    def run_require_async(self, target_component, on_success_callback=None):
        if self.thread and self.thread.isRunning():
            return

        self.set_ui_busy(True)
        if self.status_label:
            self.status_label.setText(f"Status: Processing {target_component}...")

        self.thread = QThread()
        self.worker = StateWorker(self.main_window.motor, target_component)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        
        def handle_finished():
            self.set_ui_busy(False)
            if self.status_label:
                self.status_label.setText("Status: Ready")
            if on_success_callback and callable(on_success_callback):
                on_success_callback()
            self.cleanup_thread()

        def handle_error(err_msg):
            self.set_ui_busy(False)
            if self.status_label:
                self.status_label.setText(f"Error: {err_msg}")
            self.cleanup_thread()

        self.worker.finished.connect(handle_finished)
        self.worker.error.connect(handle_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_progress(self, msg):
        if self.status_label:
            self.status_label.setText(f"Status: {msg}")

    def cleanup_thread(self):
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.thread = None
        self.worker = None

    def refresh(self):
        motor = self.main_window.motor
        if motor:
            if self.current_view_mode == "mesh":
                if not motor.motor_state_manager.ready_state.mesh:
                    self.run_require_async("mesh", self.refresh_content)
                else:
                    if hasattr(self, 'refresh_content') and callable(self.refresh_content):
                        self.refresh_content()
            elif self.current_view_mode == "material":
                if not motor.motor_state_manager.ready_state.reluctance_network:
                    self.run_require_async("reluctance_network", self.refresh_content)
                else:
                    if hasattr(self, 'refresh_content') and callable(self.refresh_content):
                        self.refresh_content()

    def closeEvent(self, event):
        self.cleanup_thread()
        super().closeEvent(event)