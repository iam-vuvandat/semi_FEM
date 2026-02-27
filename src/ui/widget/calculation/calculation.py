import paths
import numpy as np
import time
from PyQt5.QtWidgets import QWidget, QToolBar, QAction, QStyle, QApplication
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
from pyvistaqt import QtInteractor
from src.ui.widget.calculation.init_ui import init_ui

class SolverWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str, int)
    error = pyqtSignal(str)

    def __init__(self, motor):
        super().__init__()
        self.motor = motor
        self._is_cancelled = False
        self._last_update = 0

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        try:
            def thread_callback(msg, val=None):
                if self._is_cancelled:
                    raise InterruptedError("User cancelled the solver")
                
                curr = time.time()
                if curr - self._last_update > 0.2 or val == 100:
                    self.progress.emit(msg, val if val is not None else -1)
                    self._last_update = curr
            
            self.motor.analysis_motor(callback=thread_callback)
            self.finished.emit()
        except InterruptedError:
            self.error.emit("Solver stopped by user.")
        except Exception as e:
            self.error.emit(str(e))

class Calculation(QWidget):
    def __init__(self, parent_widget):
        super().__init__(parent_widget)
        self.parent_widget = parent_widget
        self.main_window = self.parent_widget.main_window
        self.motor = self.main_window.motor
        
        self.left_panel = None 
        self.btn_run = None
        self.btn_cancel = None
        self.status_label = None
        self.viz_layout = None
        self.plotter = None
        self.viewer_state = None
        
        self.thread = None
        self.worker = None
        
        self.init_ui()

    def init_ui(self):
        init_ui(calculation_tab=self)
        self.plotter = QtInteractor(self.viz_container)
        self.viz_layout.addWidget(self.plotter)
        self.plotter.set_background("white")
        self.init_toolbar()
        
        self.btn_run.clicked.connect(self.run_solver)
        self.btn_cancel.clicked.connect(self.cancel_solver)

    def init_toolbar(self):
        self.toolbar = QToolBar()
        self.toolbar.setStyleSheet("background: #f0f0f0; border-bottom: 1px solid #dcdcdc;")
        self.viz_layout.insertWidget(0, self.toolbar)

        self.act_bmap = QAction("B-Map", self)
        self.act_bmap.setCheckable(True)
        self.act_bmap.setChecked(True)
        self.act_bmap.triggered.connect(self.update_bmap)
        self.toolbar.addAction(self.act_bmap)
        
        self.act_sym = QAction("Symmetry", self)
        self.act_sym.setCheckable(True)
        self.act_sym.triggered.connect(self.update_sym)
        self.toolbar.addAction(self.act_sym)
        
        self.toolbar.addSeparator()

        self.add_slice_ui("R", "show_i", "pos_i", "max_i")
        self.add_slice_ui("Th", "show_j", "pos_j", "max_j")
        self.add_slice_ui("Z", "show_k", "pos_k", "max_k")
        
        self.toolbar.addSeparator()
        
        self.act_play = QAction(self.style().standardIcon(QStyle.SP_MediaPlay), "", self)
        self.act_play.triggered.connect(self.toggle_play)
        self.toolbar.addAction(self.act_play)

    def add_slice_ui(self, label, attr_show, attr_pos, attr_max):
        act = QAction(label, self)
        act.setCheckable(True)
        act.triggered.connect(lambda s: self.sync_state(attr_show, s))
        self.toolbar.addAction(act)
        
        dec = QAction("-", self)
        dec.triggered.connect(lambda: self.sync_state(attr_pos, -1, delta=True, max_attr=attr_max))
        self.toolbar.addAction(dec)
        
        inc = QAction("+", self)
        inc.triggered.connect(lambda: self.sync_state(attr_pos, 1, delta=True, max_attr=attr_max))
        self.toolbar.addAction(inc)

    def sync_state(self, attr, val, delta=False, max_attr=None):
        if self.viewer_state:
            if delta:
                curr = getattr(self.viewer_state, attr)
                limit = getattr(self.viewer_state, max_attr)
                setattr(self.viewer_state, attr, np.clip(curr + val, 0, limit - 1))
            else:
                setattr(self.viewer_state, attr, val)
            self.viewer_state.render()

    def update_bmap(self, state): 
        if self.viewer_state:
            self.viewer_state.bmap_mode = state
            self.viewer_state.render()
        
    def update_sym(self, state): 
        if self.viewer_state: 
            self.viewer_state.use_symmetry = state
            if hasattr(self.viewer_state, '_update_limits'):
                self.viewer_state._update_limits()
            self.viewer_state.render()

    def toggle_play(self):
        if self.viewer_state:
            if self.viewer_state.timer.isActive():
                self.viewer_state.timer.stop()
                self.act_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            else:
                self.viewer_state.timer.start(100)
                self.act_play.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def run_solver(self):
        self.refresh_tab() 
        
        self.btn_run.setEnabled(False)
        self.btn_run.setText("Solving...")
        self.btn_cancel.setEnabled(True)
        
        QApplication.processEvents()

        self.thread = QThread()
        self.worker = SolverWorker(self.motor)
        self.worker.moveToThread(self.thread)
        
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()

    def cancel_solver(self):
        if self.worker:
            self.worker.cancel()
            self.status_label.setText("Status: Cancelling...")
            self.btn_cancel.setEnabled(False)

    def on_progress(self, msg, val):
        status_text = f"Status: {msg}"
        if val >= 0:
            status_text += f" ({val}%)"
        self.status_label.setText(status_text)

    def on_error(self, message):
        self.status_label.setText(f"Info: {message}")
        self.restore_ui_state()
        self.cleanup_thread()

    def on_finished(self):
        self.status_label.setText("Status: Analysis Completed Successfully (100%)")
        self.restore_ui_state()
        
        if self.plotter:
            self.plotter.clear()
        self.viewer_state = self.motor.reluctance_network.display(plotter=self.plotter)
        self.cleanup_thread()

    def restore_ui_state(self):
        self.btn_run.setEnabled(True)
        self.btn_run.setText("Run Solver")
        self.btn_cancel.setEnabled(False)

    def cleanup_thread(self):
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()
        self.thread = None
        self.worker = None

    def refresh_tab(self):
        if self.status_label:
            self.status_label.setText("Status: Initializing solver...")
        if self.plotter:
            self.plotter.clear()
            self.plotter.render()
        if self.viewer_state and hasattr(self.viewer_state, 'timer'):
            if self.viewer_state.timer.isActive():
                self.viewer_state.timer.stop()

    def closeEvent(self, event):
        if self.viewer_state and hasattr(self.viewer_state, 'timer'):
            if self.viewer_state.timer.isActive():
                self.viewer_state.timer.stop()
        self.cleanup_thread()
        super().closeEvent(event)