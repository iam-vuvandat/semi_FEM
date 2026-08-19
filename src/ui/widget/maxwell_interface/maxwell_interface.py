import paths
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from src.ui.widget.maxwell_interface.init_ui import init_ui

# 1. Worker xu ly viec export trong luong con
class MaxwellWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str, int)
    error = pyqtSignal(str)

    def __init__(self, motor):
        super().__init__()
        self.motor = motor

    def run(self):
        try:
            def thread_callback(msg, val=None):
                # Day thong tin trang thai ve UI
                self.progress.emit(msg, val if val is not None else -1)
            
            # Goi ham export voi co che callback (neu ham export cua ban ho tro)
            # Neu motor.export_to_maxwell chua co callback, no van se chay ngam duoc
            if hasattr(self.motor, 'export_to_rmxprt'):
                self.motor.export_to_rmxprt(callback=thread_callback)
            
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class MaxwellInterface(QWidget):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.main_window = self.parent_widget.main_window
        self.motor = self.main_window.motor
        
        # Cac thuoc tinh UI duoc khoi tao trong init_ui
        self.connect_button = None
        self.status_label = None
        
        self.thread = None
        self.worker = None
        
        self.init_ui()

    def init_ui(self):
        return init_ui(maxwell_tab=self)

    def run_export(self):
        """Phuong thuc kich hoat luong con (giong run_solver)"""
        if self.motor is None:
            return

        self.connect_button.setEnabled(False)
        self.connect_button.setText("Connecting...")
        
        self.thread = QThread()
        self.worker = MaxwellWorker(self.motor)
        self.worker.moveToThread(self.thread)
        
        # Ket noi cac Signal
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        
        self.thread.start()

    def on_progress(self, msg, val):
        status_text = f"Status: {msg}"
        if val >= 0:
            status_text += f" ({val}%)"
        self.status_label.setText(status_text)

    def on_error(self, message):
        self.status_label.setText(f"Error: {message}")
        self.connect_button.setEnabled(True)
        self.connect_button.setText("Connect to Maxwell")
        self.cleanup_thread()

    def on_finished(self):
        self.status_label.setText("Status: Export to Maxwell Completed")
        self.connect_button.setEnabled(True)
        self.connect_button.setText("Connect to Maxwell")
        self.cleanup_thread()

    def cleanup_thread(self):
        if self.thread:
            self.thread.quit()
            self.thread.wait()
            self.thread = None
            self.worker = None

    def closeEvent(self, event):
        self.cleanup_thread()
        super().closeEvent(event)