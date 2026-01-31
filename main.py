import paths
import sys
import multiprocessing
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import từ cấu trúc dự án của bạn
from src.ui.main_window.core.main_window import MainWindow

if __name__ == "__main__":
    # 1. BẮT BUỘC: Hỗ trợ đa tiến trình khi đóng gói EXE
    # Đảm bảo các tác vụ tính toán máy điện không làm khởi động lại App vô hạn
    multiprocessing.freeze_support()

    # 2. Cấu hình High DPI Scaling (Tối ưu cho màn hình Surface Pro 5)
    # Phải đặt TRƯỚC khi khởi tạo QApplication
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 3. Khởi tạo ứng dụng Qt
    app = QApplication(sys.argv)
    
    # Thiết lập Font chữ hệ thống (Giữ nguyên cấu hình của bạn)
    app.setFont(QFont("Segoe UI", 9))

    # 4. Khởi tạo và hiển thị cửa sổ chính
    window = MainWindow()
    
    # Thiết lập trạng thái cửa sổ phóng to tối đa
    window.setWindowState(Qt.WindowMaximized)
    window.show()

    # 5. Vòng lặp sự kiện
    # Mọi lệnh print() trong các module khác sẽ hiển thị tại Terminal khi App đang chạy
    sys.exit(app.exec_())

    """
    
    pyinstaller --console --clean --name "semiFEM_Solver" --collect-submodules scipy --collect-all pyvista --collect-all vtk --collect-all pyvistaqt --hidden-import scipy.sparse.csgraph._validation --hidden-import scipy.special._cdflib main.py

    """