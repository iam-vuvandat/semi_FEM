import sys
import numpy as np
import pyvista as pv
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QGridLayout, QScrollArea)
from pyvistaqt import QtInteractor
from PyQt5.QtCore import Qt

class ElementDebugger(QMainWindow):
    def __init__(self, reluctance_network, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Axial Flux Motor - Full Element Inspector (Scrollable)")
        self.resize(1600, 950)

        self.reluctance_network = reluctance_network
        self.elements_3d = reluctance_network.elements
        self.grid = reluctance_network.mesh.to_pyvista_grid()
        
        # Lấy kích thước mảng 3D
        self.ni, self.nj, self.nk = self.elements_3d.shape
        self.curr_i, self.curr_j, self.curr_k = self.ni // 2, 0, self.nk // 2

        # Gán tọa độ (i, j, k) vào từng cell của PyVista để truy vấn khi click
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

        # --- PHẦN BÊN TRÁI: HIỂN THỊ 3D (2/3 màn hình) ---
        self.plotter = QtInteractor(self)
        main_layout.addWidget(self.plotter.interactor, stretch=2)

        # --- PHẦN BÊN PHẢI: BẢNG ĐIỀU KHIỂN CÓ THANH CUỘN (1/3 màn hình) ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        main_layout.addWidget(scroll_area, stretch=1)

        # Container bên trong ScrollArea
        control_container = QWidget()
        control_layout = QVBoxLayout(control_container)
        scroll_area.setWidget(control_container)

        # 1. Hiển thị Tọa độ hiện tại
        self.pos_label = QLabel("Index: [0, 0, 0]")
        self.pos_label.setStyleSheet("font-weight: bold; font-size: 26px; color: #2E86C1; margin-bottom: 5px;")
        control_layout.addWidget(self.pos_label)

        # 2. Các nút điều khiển di chuyển R, T, Z
        grid_buttons = QGridLayout()
        control_layout.addLayout(grid_buttons)
        btn_style = "padding: 15px; font-weight: bold; font-size: 16px; background-color: #EBF5FB; border: 1px solid #AED6F1;"
        
        # (Text, di, dj, dk, row, col)
        nav_configs = [
            ("R +", 1,0,0, 0,0), ("R -", -1,0,0, 0,1),
            ("T +", 0,1,0, 1,0), ("T -", 0,-1,0, 1,1),
            ("Z +", 0,0,1, 2,0), ("Z -", 0,0,-1, 2,1)
        ]

        for txt, di, dj, dk, r, c in nav_configs:
            btn = QPushButton(txt)
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(lambda ch, d=(di,dj,dk): self.move_idx(*d))
            grid_buttons.addWidget(btn, r, c)

        # 3. Khu vực hiển thị thuộc tính chi tiết
        info_title = QLabel("Chi tiết thuộc tính (Attributes):")
        info_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 20px; color: #D35400;")
        control_layout.addWidget(info_title)

        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setMinimumHeight(800) # Ép chiều cao tối thiểu lớn để chứa danh sách dài
        self.info_box.setStyleSheet("""
            background-color: #1C2833; 
            font-family: 'Consolas', 'Courier New', monospace; 
            font-size: 15px; 
            color: #FDFEFE;
            border: 2px solid #34495E;
            padding: 10px;
        """)
        control_layout.addWidget(self.info_box)

    def _init_mesh_display(self):
        """Khởi tạo màu sắc vật liệu cho toàn bộ lưới."""
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
        # Trắng (Air), Xanh (Iron), Cam (Magnet), Nâu (Coil)
        colors = ["#FFFFFF", "#3498DB", "#E67E22", "#A93226"]
        
        for mid, col in enumerate(colors):
            try:
                sub = self.grid.threshold([mid, mid], scalars="MatID")
                op = 0.05 if mid == 0 else 0.6
                self.plotter.add_mesh(sub, color=col, opacity=op, show_edges=(mid!=0), 
                                      edge_color="#2C3E50", name=f"mat_{mid}", pickable=False)
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
        """Cập nhật highlight và in tất cả thuộc tính của phần tử."""
        self.pos_label.setText(f"Index: [{self.curr_i}, {self.curr_j}, {self.curr_k}]")
        el = self.elements_3d[self.curr_i, self.curr_j, self.curr_k]
        
        if el is None:
            self.info_box.setText("No Element Data at this position.")
            return

        lines = [f"--- [ FULL DATA INSPECTION ] ---", ""]
        
        # Quét tất cả các thuộc tính của đối tượng element
        # sorted() để các thuộc tính hiện theo thứ tự bảng chữ cái cho dễ tìm
        attrs = sorted([a for a in dir(el) if not a.startswith('__')])

        for attr in attrs:
            val = getattr(el, attr)
            
            # Bỏ qua nếu là hàm (method)
            if callable(val):
                continue

            # Xử lý hiển thị dựa trên kiểu dữ liệu
            if isinstance(val, (int, float, bool, str, np.number)):
                # Làm tròn 6 chữ số nếu là số thực
                if isinstance(val, (float, np.floating)):
                    display_val = f"{val:.6g}"
                else:
                    display_val = str(val)
            elif isinstance(val, (np.ndarray, list, tuple)):
                # In mảng tường minh (có làm tròn)
                try:
                    display_val = f"\n{np.round(val, 6)}"
                except:
                    display_val = str(val)
            else:
                # Nếu là đối tượng phức tạp (Object)
                display_val = "Object"

            lines.append(f"{attr:<24}: {display_val}")

        self.info_box.setText("\n".join(lines))

        # Highlight cell được chọn
        idx = self.curr_i + self.curr_j*self.ni + self.curr_k*self.ni*self.nj
        selected_cell = self.grid.extract_cells([idx])
        self.plotter.add_mesh(selected_cell, color="#F1C40F", name="high_light_vol", opacity=1.0)
        self.plotter.add_mesh(selected_cell, color="#E74C3C", style='wireframe', line_width=10, name="high_light_wire")

def display_elements(reluctance_network):
    """Hàm tiện ích để gọi debugger từ bên ngoài."""
    app = QApplication.instance() or QApplication(sys.argv)
    window = ElementDebugger(reluctance_network)
    window.show()
    app.exec_()