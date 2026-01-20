import sys
import ctypes
from PyQt5.QtWidgets import QMainWindow, QWidget, QTabWidget, QApplication
from PyQt5.QtCore import Qt

class MainTab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_motor = None
        self.setWindowTitle("MBGRN 3D Solver - HUST")
        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.setCentralWidget(self.tabs)
        
        self.tabs.addTab(QWidget(), "📁 Library")
        self.tabs.addTab(QWidget(), "🏗️ Setup")
        self.tabs.addTab(QWidget(), "⚡ Solver")
        self.tabs.addTab(QWidget(), "📊 Results")

if __name__ == "__main__":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    window = MainTab()
    window.showMaximized()
    
    sys.exit(app.exec_())