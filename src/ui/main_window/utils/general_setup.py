import sys
import ctypes
import os
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

def general_setup(main_window=None, app=None):
    try:
        # 1. Định danh App ID để Windows không gộp nhầm với Python
        myappid = 'semiFEM.v0.0.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    # 2. Thiết lập đường dẫn tới file .ico
    # Đảm bảo bạn đã đổi tên logo.png thành logo.ico sau khi convert
    icon_path = os.path.join('src', 'ui', 'assets', 'logo.png')
    
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
    else:
        # Fallback nếu không tìm thấy file .ico
        app_icon = QIcon()

    if app is not None:
        # Thiết lập icon cho toàn bộ ứng dụng
        app.setWindowIcon(app_icon)
        # Đồng nhất giao diện Fusion
        app.setStyle(QStyleFactory.create('Fusion'))

    if main_window is not None:
        # 3. Tiêu đề và Icon cho cửa sổ chính
        main_window.setWindowTitle("semiFEM")
        main_window.setWindowIcon(app_icon)
        
        # 4. Tự động phóng to cửa sổ
        main_window.setWindowState(Qt.WindowMaximized)
        
        # 5. Kích thước tối thiểu cho 3D-MBGRN Solver
        main_window.setMinimumSize(1024, 768)