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

    version_label = QLabel("Maxwell Version:")
    maxwell_tab.version_combo = QComboBox()
    maxwell_tab.version_combo.addItems(["2023R1"])
    
    maxwell_tab.connect_button = QPushButton("Connect to Maxwell")
    maxwell_tab.connect_button.setFixedHeight(30)
    
    maxwell_tab.connect_button.clicked.connect(maxwell_tab.run_export)
    
    left_layout.addWidget(version_label)
    left_layout.addWidget(maxwell_tab.version_combo)
    left_layout.addSpacing(5)
    left_layout.addWidget(maxwell_tab.connect_button)
    left_layout.addStretch() 

    # --- RIGHT PANEL: EMPTY ---
    right_widget = QFrame()
    right_widget.setFrameShape(QFrame.StyledPanel)

    content_splitter.addWidget(left_widget)
    content_splitter.addWidget(right_widget)
    content_splitter.setStretchFactor(1, 4) 

    main_layout.addWidget(content_splitter, 1)

    # 3. --- BOTTOM: STATUS BAR ---
    status_container = QFrame()
    status_container.setFixedHeight(30)
    status_container.setFrameShape(QFrame.StyledPanel)
    status_layout = QHBoxLayout(status_container)
    status_layout.setContentsMargins(10, 0, 10, 0)

    maxwell_tab.status_label = QLabel("Status: Ready")
    status_layout.addWidget(maxwell_tab.status_label)
    status_layout.addStretch()

    main_layout.addWidget(status_container, 0)

    return None