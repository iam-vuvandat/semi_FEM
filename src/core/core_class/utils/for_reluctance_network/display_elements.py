import sys
import numpy as np
import pyvista as pv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QLabel, QTextEdit, QGridLayout)
from pyvistaqt import QtInteractor
from PyQt5.QtGui import QFont

class ElementDebugger(QMainWindow):
    def __init__(self, reluctance_network, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Axial Flux Motor - Full Element Inspector (Large Font)")
        self.resize(1500, 950) # Tăng kích thước cửa sổ mặc định

        self.reluctance_network = reluctance_network
        self.elements_3d = reluctance_network.elements
        self.grid = reluctance_network.mesh.to_pyvista_grid()
        
        self.ni, self.nj, self.nk = self.elements_3d.shape
        self.curr_i, self.curr_j, self.curr_k = self.ni // 2, 0, self.nk // 2

        idx_i, idx_j, idx_k = np.meshgrid(np.arange(self.ni), np.arange(self.nj), np.arange(self.nk), indexing='ij')
        self.grid.cell_data["idx_i"] = idx_i.flatten(order='F')
        self.grid.cell_data["idx_j"] = idx_j.flatten(order='F')
        self.grid.cell_data["idx_k"] = idx_k.flatten(order='F')

        self._setup_ui()
        self._init_mesh_display()
        self.update_selection()

    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- LEFT: 3D VIEW ---
        self.plotter = QtInteractor(self)
        main_layout.addWidget(self.plotter.interactor, stretch=2)

        # --- RIGHT: CONTROL & INFO ---
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        main_layout.addWidget(control_panel, stretch=1)

        # Nhãn tọa độ (Cỡ 22px)
        self.pos_label = QLabel("Position: [0, 0, 0]")
        self.pos_label.setStyleSheet("font-weight: bold; font-size: 24px; color: #1a5276; margin-bottom: 10px;")
        control_layout.addWidget(self.pos_label)

        # Nút điều khiển (Cỡ chữ 18px, padding lớn)
        grid_buttons = QGridLayout()
        control_layout.addLayout(grid_buttons)
        btn_style = "padding: 15px; font-weight: bold; font-size: 18px; min-width: 80px;"
        
        self.btn_r_plus = QPushButton("R +"); self.btn_r_plus.setStyleSheet(btn_style)
        self.btn_r_minus = QPushButton("R -"); self.btn_r_minus.setStyleSheet(btn_style)
        self.btn_t_plus = QPushButton("T +"); self.btn_t_plus.setStyleSheet(btn_style)
        self.btn_t_minus = QPushButton("T -"); self.btn_t_minus.setStyleSheet(btn_style)
        self.btn_z_plus = QPushButton("Z +"); self.btn_z_plus.setStyleSheet(btn_style)
        self.btn_z_minus = QPushButton("Z -"); self.btn_z_minus.setStyleSheet(btn_style)

        self.btn_r_plus.clicked.connect(lambda: self.move_idx(1, 0, 0))
        self.btn_r_minus.clicked.connect(lambda: self.move_idx(-1, 0, 0))
        self.btn_t_plus.clicked.connect(lambda: self.move_idx(0, 1, 0))
        self.btn_t_minus.clicked.connect(lambda: self.move_idx(0, -1, 0))
        self.btn_z_plus.clicked.connect(lambda: self.move_idx(0, 0, 1))
        self.btn_z_minus.clicked.connect(lambda: self.move_idx(0, 0, -1))

        grid_buttons.addWidget(self.btn_r_plus, 0, 0); grid_buttons.addWidget(self.btn_r_minus, 0, 1)
        grid_buttons.addWidget(self.btn_t_plus, 1, 0); grid_buttons.addWidget(self.btn_t_minus, 1, 1)
        grid_buttons.addWidget(self.btn_z_plus, 2, 0); grid_buttons.addWidget(self.btn_z_minus, 2, 1)

        # Nhãn tiêu đề thông tin
        info_title = QLabel("Chi tiết thuộc tính (Attributes):")
        info_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 15px;")
        control_layout.addWidget(info_title)

        # Bảng thông tin (Cỡ chữ 16px)
        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setStyleSheet("""
            background-color: #f4f6f7; 
            font-family: 'Consolas', 'Courier New'; 
            font-size: 16px; 
            color: #212f3d;
            border: 1px solid #bdc3c7;
            padding: 10px;
        """)
        control_layout.addWidget(self.info_box)

    def _init_mesh_display(self):
        mat_ids = np.zeros(self.grid.n_cells)
        for i in range(self.ni):
            for j in range(self.nj):
                for k in range(self.nk):
                    el = self.elements_3d[i, j, k]
                    if el:
                        m = str(el.material).lower()
                        idx = i + j*self.ni + k*self.ni*self.nj
                        if "iron" in m: mat_ids[idx] = 1
                        elif "magnet" in m: mat_ids[idx] = 2
                        elif "coil" in m or "winding" in m: mat_ids[idx] = 3
        
        self.grid.cell_data["MatID"] = mat_ids
        colors = ["#FFFFFF", "#A5C5E5", "#FF9900", "#BC8E8E"]
        
        for mid, col in enumerate(colors):
            try:
                sub = self.grid.threshold([mid, mid], scalars="MatID")
                op = 0.05 if mid == 0 else 0.7
                self.plotter.add_mesh(sub, color=col, opacity=op, show_edges=(mid!=0), 
                                      edge_color="#444444", name=f"mat_{mid}", pickable=False)
            except: pass

        self.plotter.view_isometric()
        self.plotter.enable_cell_picking(callback=self._on_pick, show=False)

    def move_idx(self, di, dj, dk):
        self.curr_i = np.clip(self.curr_i + di, 0, self.ni - 1)
        self.curr_j = (self.curr_j + dj) % self.nj
        self.curr_k = np.clip(self.curr_k + dk, 0, self.nk - 1)
        self.update_selection()

    def _on_pick(self, cell):
        if cell is None: return
        self.curr_i = int(cell.cell_data["idx_i"][0])
        self.curr_j = int(cell.cell_data["idx_j"][0])
        self.curr_k = int(cell.cell_data["idx_k"][0])
        self.update_selection()

    def update_selection(self):
        self.pos_label.setText(f"Index: [{self.curr_i}, {self.curr_j}, {self.curr_k}]")
        el = self.elements_3d[self.curr_i, self.curr_j, self.curr_k]
        
        if el is None:
            self.info_box.setText("No Element Data")
            return

        def fmt(val, precision=4):
            if val is None: return "N/A"
            return np.round(val, precision)

        lines = []
        lines.append(f"--- [ BASIC INFO ] ---")
        lines.append(f"material      : {el.material}")
        lines.append(f"flat_position : {el.flat_position}")
        lines.append(f"volume_error  : {fmt(el.volume_error, 8)}")
        
        lines.append(f"\n--- [ GEOMETRY ] ---")
        lines.append(f"length (dr, dt, dz):\n{fmt(el.length, 6)}")
        lines.append(f"section_area (Ar, At, Az):\n{fmt(el.section_area, 8)}")
        lines.append(f"length_ratio  : {fmt(el.length_ratio)}")
        
        lines.append(f"\n--- [ MAGNETIC SOURCES ] ---")
        lines.append(f"winding_current: {fmt(el.winding_current)}")
        lines.append(f"winding_source (MMF):\n{fmt(el.winding_source)}")
        lines.append(f"magnet_source (MMF):\n{fmt(el.magnet_source)}")
        lines.append(f"magnetic_source (Total):\n{fmt(el.magnetic_source)}")

        lines.append(f"\n--- [ RELUCTANCE ] ---")
        lines.append(f"ur (permeability): {fmt(el.relative_permeability, 2)}")
        lines.append(f"reluctance (Current):\n{fmt(el.reluctance, 2)}")

        lines.append(f"\n--- [ RESULTS ] ---")
        lines.append(f"B_average: {fmt(el.flux_density_average, 4)} T")
        lines.append(f"Flux Direct:\n{fmt(el.flux_direct, 8)}")

        self.info_box.setText("\n".join(lines))

        idx = self.curr_i + self.curr_j*self.ni + self.curr_k*self.ni*self.nj
        selected_cell = self.grid.extract_cells([idx])
        self.plotter.add_mesh(selected_cell, color="#F1C40F", name="high_light_vol", opacity=1.0) # Sáng vàng rực
        self.plotter.add_mesh(selected_cell, color="#E74C3C", style='wireframe', line_width=8, name="high_light_wire") # Khung đỏ đậm

def display_elements(reluctance_network):
    app = QApplication.instance() or QApplication(sys.argv)
    window = ElementDebugger(reluctance_network)
    window.show()
    app.exec_()
    return None