import paths
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QLabel, QScrollArea, QGroupBox, QComboBox, 
                             QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(winding_tab=None):
    if winding_tab is None:
        return None

    main_win = winding_tab.main_window
    motor = main_win.motor
    winding_data = motor.winding_data 
    
    def clear_layout(layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def create_matrix_widget(matrix):
        table = QTableWidget()
        if matrix is not None:
            rows, cols = matrix.shape
            table.setRowCount(rows)
            table.setColumnCount(cols)
            table.setHorizontalHeaderLabels([f"Ph {chr(65+i)}" for i in range(cols)])
            table.setVerticalHeaderLabels([f"Slot {i+1}" for i in range(rows)])
            
            for i in range(rows):
                for j in range(cols):
                    val = matrix[i, j]
                    item = QTableWidgetItem(f"{val:g}")
                    item.setTextAlignment(Qt.AlignCenter)
                    if val > 0:
                        item.setBackground(QColor("#FFF59D"))
                    elif val < 0:
                        item.setBackground(QColor("#81D4FA"))
                    table.setItem(i, j, item)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    def create_plot_widget(fig):
        if fig is None:
            lbl = QLabel("No Plot Data. Check parameters or Slot/Pole combination.")
            lbl.setAlignment(Qt.AlignCenter)
            return lbl
        canvas = FigureCanvas(fig)
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return canvas

    def update_right_panel_content():
        if not hasattr(winding_tab, 'view_selector'):
            return
        mode = winding_tab.view_selector.currentText()
        clear_layout(winding_tab.right_content_layout)
        
        mapping = {
            "Winding Matrix (Ampe-turns)": ("matrix", "slot_matrix"),
            "Tooth Matrix (MMF Potential)":("matrix", "winding_matrix"),
            "Layout Plot (Linear)":        ("plot", "fig_layout"),
            "Polar Plot (Circular)":       ("plot", "fig_polar"),
            "Star of Slots (Phasors)":     ("plot", "fig_star"),
            "MMF Distribution":            ("plot", "fig_mmf"),
            "Winding Factors":             ("plot", "fig_wf")
        }
        
        data_type, attr_name = mapping.get(mode, (None, None))
        if data_type == "matrix":
            matrix = getattr(winding_data, attr_name, None)
            widget = create_matrix_widget(matrix)
            winding_tab.right_content_layout.addWidget(widget)
        elif data_type == "plot":
            fig = getattr(winding_data, attr_name, None)
            widget = create_plot_widget(fig)
            winding_tab.right_content_layout.addWidget(widget)

    def handle_refresh():
        if motor is None:
            return
        if motor.motor_state_manager.ready_state.winding_data:
            update_right_panel_content()
            return
            
        motor.require("winding_data")
        update_right_panel_content()

    def global_update():
        if motor is None:
            return
        motor.just_changed("winding_data")
        handle_refresh()
        QApplication.processEvents()

    winding_tab.refresh = handle_refresh
    winding_tab.refresh_content = update_right_panel_content

    main_layout = QHBoxLayout(winding_tab)
    main_layout.setContentsMargins(10, 10, 10, 10)
    
    splitter = QSplitter(Qt.Horizontal)

    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(0, 0, 5, 0)
    
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    
    content_widget = QWidget()
    content_vbox = QVBoxLayout(content_widget) 
    content_vbox.setAlignment(Qt.AlignTop)

    def create_group(title, attrs):
        grp = QGroupBox(title)
        layout = QFormLayout(grp)
        layout.setVerticalSpacing(10)
        for attr, lbl in attrs:
            if hasattr(winding_data, attr):
                input_w = bind_input(winding_data, attr, 1.0, global_update)
                input_w.setFixedWidth(80)
                layout.addRow(f"{lbl}:", input_w)
        return grp

    content_vbox.addWidget(create_group("Topology", [
        ("phase", "Phases"), 
        ("winding_layer", "Layers"), 
        ("parallel_path", "Parallel Paths")
    ]))
    content_vbox.addWidget(create_group("Coil Params", [
        ("turns", "Turns/Coil"), 
        ("throw", "Coil Throw")
    ]))
    content_vbox.addStretch()
    
    scroll.setWidget(content_widget)
    left_layout.addWidget(scroll)

    right_panel = QFrame()
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(5, 0, 0, 0)

    header_layout = QHBoxLayout()
    header_lbl = QLabel("Display Mode:")
    
    winding_tab.view_selector = QComboBox()
    winding_tab.view_selector.addItems([
        "Winding Matrix (Ampe-turns)", "Tooth Matrix (MMF Potential)", "Layout Plot (Linear)",
        "Polar Plot (Circular)", "Star of Slots (Phasors)", "MMF Distribution", "Winding Factors"
    ])
    winding_tab.view_selector.currentIndexChanged.connect(update_right_panel_content)
    
    header_layout.addWidget(header_lbl)
    header_layout.addWidget(winding_tab.view_selector)
    header_layout.addStretch()
    
    winding_tab.right_content_widget = QWidget()
    winding_tab.right_content_layout = QVBoxLayout(winding_tab.right_content_widget)
    winding_tab.right_content_layout.setContentsMargins(0, 10, 0, 0)

    right_layout.addLayout(header_layout)
    right_layout.addWidget(winding_tab.right_content_widget)

    splitter.addWidget(left_panel)
    splitter.addWidget(right_panel)
    
    splitter.setSizes([400, 600])
    splitter.setStretchFactor(0, 2)
    splitter.setStretchFactor(1, 3) 
    
    main_layout.addWidget(splitter)
    
    QTimer.singleShot(100, handle_refresh)
    
    return None