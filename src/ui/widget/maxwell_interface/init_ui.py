import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, 
                             QFrame, QPushButton, QLabel, QComboBox)
from PyQt5.QtCore import Qt

def init_ui(maxwell_tab):
    if maxwell_tab is None: 
        return None

    motor = maxwell_tab.main_window.motor
    
    # 1. Main Layout (Vertical)
    main_layout = QVBoxLayout(maxwell_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    main_layout.setSpacing(5)

    # 2. Central Content (Splitter)
    content_splitter = QSplitter(Qt.Horizontal)

    # --- LEFT PANEL: SETTINGS & ACTIONS ---
    left_widget = QWidget()
    left_layout = QVBoxLayout(left_widget)
    left_layout.setContentsMargins(0, 0, 10, 0)
    left_layout.setSpacing(10)

    # Label và Menu thả xuống chọn phiên bản
    version_label = QLabel("Maxwell Version:")
    version_label.setStyleSheet("font-size: 12px; color: #333;")
    maxwell_tab.version_combo = QComboBox()
    # Danh sách phiên bản (có thể bổ sung thêm nếu cần)
    maxwell_tab.version_combo.addItems(["2023R1"])
    
    # Nút Connect cổ điển
    maxwell_tab.connect_button = QPushButton("Connect to Maxwell")
    maxwell_tab.connect_button.setFixedHeight(30)
    
    # Kết nối sự kiện
    maxwell_tab.connect_button.clicked.connect(maxwell_tab.run_export)
    
    # Sắp xếp các Widget bên trái
    left_layout.addWidget(version_label)
    left_layout.addWidget(maxwell_tab.version_combo)
    left_layout.addSpacing(5) # Tạo khoảng cách nhỏ giữa combo và nút bấm
    left_layout.addWidget(maxwell_tab.connect_button)
    left_layout.addStretch() 

    # --- RIGHT PANEL: EMPTY ---
    right_widget = QFrame()
    right_widget.setFrameShape(QFrame.StyledPanel)
    right_widget.setStyleSheet("background-color: #ffffff; border: 1px solid #dcdcdc;")

    content_splitter.addWidget(left_widget)
    content_splitter.addWidget(right_widget)
    content_splitter.setStretchFactor(1, 4) 

    main_layout.addWidget(content_splitter, 1)

    # 3. --- BOTTOM: STATUS BAR ---
    status_container = QFrame()
    status_container.setFixedHeight(30)
    status_container.setStyleSheet("background-color: #f8f8f8; border-top: 1px solid #dcdcdc;")
    status_layout = QHBoxLayout(status_container)
    status_layout.setContentsMargins(10, 0, 10, 0)

    maxwell_tab.status_label = QLabel("Status: Ready")
    maxwell_tab.status_label.setStyleSheet("font-size: 13px; color: #333;")
    status_layout.addWidget(maxwell_tab.status_label)
    status_layout.addStretch()

    main_layout.addWidget(status_container, 0)

    return None