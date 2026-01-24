import ctypes
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtCore import Qt

def general_setup(main_window = None):
    # 1. Cấu hình App ID để hiển thị icon đúng trên Taskbar Windows
    try:
        myappid = 'hust.ee.mbgrn.3d.solver.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    if main_window is not None:
        # 2. Thiết lập tiêu đề cửa sổ
        main_window.setWindowTitle("semiFem - 3D MBGRN Solver")
        
        # 3. TỰ ĐỘNG PHÓNG TO TOÀN MÀN HÌNH
        # Cách 1: Phóng to cửa sổ nhưng vẫn để lại thanh Taskbar (Khuyên dùng)
        main_window.setWindowState(Qt.WindowMaximized)
        
        # Cách 2: Toàn màn hình hoàn toàn, che cả thanh Taskbar (Thường dùng cho Game)
        # main_window.setWindowState(Qt.WindowFullScreen)

        # 4. Thiết lập Style Fusion để giao diện đồng nhất trên mọi máy
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
        # 5. Thiết lập kích thước tối thiểu (đảm bảo không bị vỡ layout khi thu nhỏ)
        main_window.setMinimumSize(1024, 768)