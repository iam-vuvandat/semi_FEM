import paths
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QSplitter, QWidget, QFormLayout, 
                             QFrame, QComboBox, QLabel, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from src.ui.widget.widget.utils.bind_input import bind_input

def init_ui(winding_tab=None):
    if winding_tab is None: return None

    motor = winding_tab.main_window.motor
    # 1. Input Parameters Container
    winding_data = motor.winding_data 
    
    main_layout = QHBoxLayout(winding_tab)
    splitter = QSplitter(Qt.Horizontal)

    # --- 1. REFRESH LOGIC: ACCESSING motor.winding_matrix ---
    def refresh_winding_ui():
        """Updates the table. Logic: uses motor.winding_matrix, NOT winding_data.winding_matrix"""
        # Recalculate the matrix in the core logic first
        motor.find_winding_matrix()
        
        # ACCESSING THE DIRECT PROPERTY OF MOTOR
        matrix = motor.winding_matrix 
        
        if matrix is None:
            winding_tab.matrix_table.setRowCount(0)
            return

        rows, cols = matrix.shape
        table = winding_tab.matrix_table
        table.setRowCount(rows)
        table.setColumnCount(cols)
        
        # Headers and data filling logic...
        headers = [f"Phase {chr(65+i)}" for i in range(cols)]
        table.setHorizontalHeaderLabels(headers)
        row_headers = [f"Slot {i+1}" for i in range(rows)]
        table.setVerticalHeaderLabels(row_headers)

        for i in range(rows):
            for j in range(cols):
                val = matrix[i, j]
                item = QTableWidgetItem(f"{val:g}")
                item.setTextAlignment(Qt.AlignCenter)
                if val > 0: item.setBackground(QColor("#FFF59D"))
                elif val < 0: item.setBackground(QColor("#81D4FA"))
                table.setItem(i, j, item)
        
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # --- 2. LEFT PANEL: INPUT BINDING TO winding_data ---
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    
    input_frame = QFrame()
    input_frame.setStyleSheet("background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px;")
    form = QFormLayout(input_frame)

    # BINDING TO THE INPUT CONTAINER
    form.addRow("Number of Phases:",    bind_input(winding_data, "phase_number", 1, refresh_winding_ui))
    form.addRow("Turns per Coil:",      bind_input(winding_data, "turns_number", 1, refresh_winding_ui))
    form.addRow("Coil Throw (y):",      bind_input(winding_data, "coil_throw", 1, refresh_winding_ui))
    form.addRow("Parallel Paths (a):",  bind_input(winding_data, "parallel_path", 1, refresh_winding_ui))
    form.addRow("Winding Layers:",      bind_input(winding_data, "winding_layer", 1, refresh_winding_ui))

    # Winding Type Combo
    type_combo = QComboBox()
    type_combo.addItems(["concentrated", "distributed"])
    type_combo.setCurrentText(winding_data.winding_type)
    
    def on_type_changed(text):
        winding_data.winding_type = text # Update input container
        motor.find_winding_matrix()      # Calculate output property
        refresh_winding_ui()
        
    type_combo.currentTextChanged.connect(on_type_changed)
    form.addRow("Winding Type:", type_combo)

    left_layout.addWidget(QLabel("<b>Winding Configuration</b>"))
    left_layout.addWidget(input_frame)
    left_layout.addStretch()

    # --- 3. RIGHT PANEL: VIEWING THE MATRIX ---
    right_container = QWidget()
    right_layout = QVBoxLayout(right_container)
    winding_tab.matrix_table = QTableWidget()
    
    right_layout.addWidget(QLabel("<b>Winding Matrix Preview (Direct Output)</b>"))
    right_layout.addWidget(winding_tab.matrix_table)

    splitter.addWidget(left_container)
    splitter.addWidget(right_container)
    splitter.setStretchFactor(0, 1)
    splitter.setStretchFactor(1, 2)
    main_layout.addWidget(splitter)

    refresh_winding_ui()
    return None